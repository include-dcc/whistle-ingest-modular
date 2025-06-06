#!/usr/bin/env python

from pathlib import Path
import csv
from argparse import ArgumentParser, FileType

import pdb
from collections import defaultdict

from rich import print

from yaml import safe_load

_missing = set(["NA", ""])


class Family:
    globalid_lookup = None

    def __init__(self, row):
        pdb.set_trace()
        self.family_id = row["Family ID"]
        self.family_type = row["Family Type"]
        self.proband_ids = set()
        self.relationships = defaultdict(set)

    def extract_id(self, row, colname):
        if row[colname] != "NA":
            if "," in row[colname]:
                ids = [x.strip() for x in row[colname].split(",")]
            else:
                ids = [x.strip() for x in row[colname].split("|")]

            for id in ids:
                self.relationships[colname].add(id)

    def add_participant(self, row):
        if self.family_id == "240":
            print(row)
            pdb.set_trace()
        id = row["Participant External ID"]
        self.extract_id(row, "Sibling ID")
        self.extract_id(row, "Father ID")
        self.extract_id(row, "Mother ID")

        relationships = [x.strip() for x in row["Family Relationship"].split(",")]
        for relationship in relationships:
            if relationship == "Proband":
                self.proband_ids.add(id)
            elif relationship == "Mother":
                self.relationships["Mother ID"].add(id)
            elif relationship == "Father":
                self.relationships["Father ID"].add(id)
            elif relationship == "Sibling":
                self.relationships["Sibling ID"].add(id)
            else:
                self.relationships[relationship].add(id)

    @classmethod
    def write_header(cls, writer):
        writer.writerow(["Family ID", "Family Type", "ID1", "ID2", "Relationship"])

    @classmethod
    def write_relationship(cls, writer, line, pid, otherid, relationship):
        if pid not in _missing and otherid not in _missing:
            writer.writerow(
                [
                    line["Family ID"],
                    line["Family Type"],
                    Family.globalid_lookup[pid],
                    Family.globalid_lookup[otherid],
                    relationship,
                ]
            )

    def write(self, writer):
        observed_probands = set()
        for proband in self.proband_ids:
            for relationship, idlist in self.relationships.items():
                # Drop the " ID" part
                relid = relationship.split(" ")[0]
                for id in idlist:
                    if id != proband and id not in observed_probands:
                        writer.writerow(
                            [
                                self.family_id,
                                self.family_type,
                                Family.globalid_lookup[id],
                                Family.globalid_lookup[proband],
                                relid,
                            ]
                        )
            observed_probands.add(proband)

            # For now, let's skip the sibling list and only create
            # relationships that involve a proband


# After talking to Robert Mar 6, 2023, I think trying to infer parent IDs is
# undesirable, so we'll not use this going forward...until we change our mind
if __name__ == "__main__":
    parser = ArgumentParser(
        description="After looking through the file, this "
        "script will attempt to create a data dictionary"
    )
    parser.add_argument(
        "config",
        nargs="+",
        type=FileType("rt"),
        help="Dataset YAML file with details required to run conversion.",
    )
    args = parser.parse_args()

    for f in args.config:
        config = safe_load(f)

        # All of the family stuff lives inside the participant table
        filename = config["dataset"]["participant"]["filename"]
        print(f"[green]Participant File '{filename}'.[/green]")

        # first, let's build our lookup to allow us to use global IDs instead
        # of relying solely on external IDs for the family intermediate file.
        Family.globalid_lookup = {}
        with Path(filename).open("rt") as participant_source:
            reader = csv.DictReader(participant_source, delimiter=",", quotechar='"')

            for line in reader:
                Family.globalid_lookup[line["Participant External ID"]] = line[
                    "Participant Global ID"
                ]

        filedir = Path(filename).parent

        family_path = filedir / "family.csv"
        print(f"[blue]Family CSV path: '{family_path}'.[/blue]")

        with family_path.open("wt") as famfile:
            fwriter = csv.writer(famfile, delimiter=",", quotechar='"')
            Family.write_header(fwriter)
            observed_siblings = set()

            with open(filename, "rt") as condf:
                participants = csv.DictReader(condf, delimiter=",", quotechar='"')

                for line in participants:
                    fid = line["Family ID"]
                    # We have two forms to consider: Family Relationships and
                    # Family Relationship Type
                    #
                    # Family Relationships have two ids and are defined by rows
                    # where Father ID, Mother ID, Sibling ID, Other..ID present
                    pid = line["Participant External ID"]
                    Family.write_relationship(
                        fwriter, line, pid, line["Father ID"], "Father"
                    )
                    Family.write_relationship(
                        fwriter, line, pid, line["Mother ID"], "Mother"
                    )

                    # Why should we expect that the data is consistent between releases? One time it's
                    # comma separated and the next it's pipes. What will we get next time?
                    if "," in line["Sibling ID"]:
                        line["Sibling ID"] = line["Sibling ID"].replace(",", "|")
                    siblings = [x.strip() for x in line["Sibling ID"].split("|")]
                    for sibling in siblings:
                        if sibling != "NA" and sibling not in observed_siblings:
                            Family.write_relationship(
                                fwriter, line, pid, sibling, "Sibling"
                            )
                    if "," in line["Other Family Member ID"]:
                        line["Other Family Member ID"] = line[
                            "Other Family Member ID"
                        ].replace(",", "|")
                    others = [
                        x.strip() for x in line["Other Family Member ID"].split("|")
                    ]
                    for other in others:
                        if other != "NA" and other not in observed_siblings:
                            Family.write_relationship(
                                fwriter, line, pid, other, "Other relative"
                            )

                    fwriter.writerow(
                        [
                            fid,
                            line["Family Type"],
                            Family.globalid_lookup[pid],
                            "NA",
                            line["Family Relationship"],
                        ]
                    )
                    observed_siblings.add(pid)
