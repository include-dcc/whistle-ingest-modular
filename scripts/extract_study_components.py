#!/usr/bin/env python

from argparse import ArgumentParser, FileType
from pathlib import Path
from csv import reader as Reader
from csv import writer as Writer

"""Walk through the study file from Pierrette and extract each of the study 
tables and their corresponding contact tables into separate files within the 
correlated table directories.
"""

study_contact_colnames = [
    "Study Code",
    "Study Contact Name",
    "Study Contact Institution",
    "Study Contact Email",
]


def run():
    parser = ArgumentParser(
        description="Extract the row associated with each study into their "
        "corresponding table directory, along with the contacts "
        "as a separate table. "
    )
    parser.add_argument(
        "study_meta",
        nargs="+",
        type=FileType("rt", encoding="cp1252"),
        help="The CSV containing all of the study metadata.",
    )
    args = parser.parse_args()

    for study in args.study_meta:
        reader = Reader(study, delimiter=",", quotechar='"')

        header = None
        contact_data_index = {}

        for line in reader:
            if header is None:
                header = line
                for colname in study_contact_colnames:
                    contact_data_index[colname] = header.index(colname)
            else:
                study_code = line[0]

                # This changed after my config was already defined
                if study_code == "X01-Hakonarson":
                    destdir = Path("data/tables") / "X01-Hakon"
                else:
                    destdir = Path("data/tables") / study_code
                destdir.mkdir(parents=True, exist_ok=True)

                study_file = destdir / "study.csv"
                with study_file.open("wt") as file:
                    writer = Writer(file, delimiter=",", quotechar='"')
                    writer.writerow(header)
                    writer.writerow(line)

                contact_details = []
                names = line[contact_data_index["Study Contact Name"]].split("|")
                institutions = line[
                    contact_data_index["Study Contact Institution"]
                ].split("|")
                emails = line[contact_data_index["Study Contact Email"]].split("|")

                contact_file = destdir / "contacts.csv"
                # Right now, multivalue fields are not consistently populated, so I can't rely on
                # this to be true.
                # if len(names) == len(institutions) == len(emails):
                if len(names) == len(emails):
                    last_inst = None
                    with contact_file.open("wt") as file:
                        writer = Writer(file, delimiter=",", quotechar='"')

                        writer.writerow(study_contact_colnames)
                        for i in range(len(names)):
                            if i < len(institutions):
                                institution = institutions[i]

                            # Because we can't get a sane model for input, we
                            # have to do our best to figure out which
                            # institution any given person belongs to
                            if institution != "":
                                last_inst = institution
                            else:
                                institution = last_inst
                            cdetails = [
                                study_code,
                                names[i],
                                institution,
                                emails[i],
                            ]
                            writer.writerow(cdetails)
                else:
                    print(line)
                    print(
                        f"No Contacts were created for this entry due to mismatched Names, institutions and emails.  "
                    )
                    print(f"Names: {names}")
                    print(f"Emails: {emails}")
                    print(f"Institutions: {institutions}")


if __name__ == "__main__":
    run()
