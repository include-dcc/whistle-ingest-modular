#!/usr/bin/env python

import sys
from csv import DictReader, writer as csv_writer
from yaml import safe_load
from argparse import ArgumentParser, FileType
from pathlib import Path

import pdb

class MissingCurie(Exception):
    def __init__(self, code, harmonizedCode):
        self.code = code
        self.harmonizedCode = harmonizedCode
        super().__init__(self.message())

    def message(self):
        return f"There was no curie associated with the code, {self.code} ({self.harmonizedCode})"


class Coding:
    fhir_system = {
        "HP": "http://purl.obolibrary.org/obo/hp.owl",
        "MONDO": "http://purl.obolibrary.org/obo/mondo.owl",
        "MAXO": "http://purl.obolibrary.org/obo/maxo.owl",
        "NCIT": "http://purl.obolibrary.org/obo/ncit.owl",
        "SNOMED": "http://snomed.info/sct",
        "SYMP": "https://purl.obolibrary.org/obo/symp.owl",
        "LOINC": "https://loinc.org/",
        "MEDDRA": "https://www.meddra.org",
        "MESH": "urn:oid:2.16.840.1.113883.6.177",
        "UCUM": "http://unitsofmeasure.org",
        "OMIT": "http://purl.obolibrary.org/obo/omit.owl",
    }

    def __init__(self, local_code, local_display, parent_varname, code, display):
        self.local_code = local_code
        self.local_display = local_display
        self.parent_varname = parent_varname
        self.display = display
        try:
            self.curie, self.code = code.split(":")
        except:
            raise MissingCurie(local_code, code)

        self.system = Coding.fhir_system[self.curie]

    def row(self):
        "local code,text,table_name,parent_varname,local code system,code,display,code system,comment"
        return [
            self.local_code,
            self.local_display,
            "condition",
            self.parent_varname,
            "condition_description",
            self.code,
            self.display,
            self.system,
            "",
        ]


def ExtractCoding(line, writer, code_colname, display_colname, observed_codes):
    code = line[code_colname]
    display = line[display_colname]

    code_key = f"{line['Condition or Measure Source Text']}-{code}"

    if code != "NA" and code != "":
        if code_key not in observed_codes:
            coding = Coding(
                line["Condition or Measure Source Text"],
                line["Condition or Measure Source Text"],
                code_colname,
                code,
                display,
            )
            writer.writerow(coding.row())
            observed_codes[code_key] = coding


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Extract harmony details for a based on the condition details described in the configuration file."
    )

    parser.add_argument(
        "config",
        nargs="+",
        type=FileType("rt"),
        help="Whistler configuration YAML file for study to be addressed. ",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Filename to write conditions to. By default, it will be harmony/{study_id}-conditions.csv",
    )
    args = parser.parse_args()

    for f in args.config:
        config = safe_load(f)

        study_id = config["study_id"]

        output_filename = args.output
        if output_filename is None:
            output_filename = f"harmony/{study_id.lower()}-conditions.csv"

        condition_filename = config["dataset"]["condition"]["filename"]
        with open(condition_filename, "rt") as cfile:
            observed_codes = {}

            with open(output_filename, "wt") as outf:
                writer = csv_writer(outf)
                writer.writerow(
                    "local code,text,table_name,parent_varname,local code system,code,display,code system,comment".split(
                        ","
                    )
                )

                # We have a few other condition related entries that we need to prepopulate
                writer.writerow(
                    "Observed,Condition was observed or reported (this will be the case for most conditions),condition,Condition Interpretation,Condition Interpretation,LA33635-6,Observed,http://loinc.org".split(
                        ","
                    )
                )
                writer.writerow(
                    "Observed,Condition was observed or reported (this will be the case for most conditions),Condition,Condition Interpretation,Condition Interpretation,confirmed,Confirmed,http://terminology.hl7.org/CodeSystem/condition-ver-status".split(
                        ","
                    )
                )
                writer.writerow(
                    "Not Observed,Not Observed,condition,Condition Interpretation,Condition Interpretation,LA19655-2,Not Observed,http://loinc.org".split(
                        ","
                    )
                )
                writer.writerow(
                    "Current,Condition is ongoing,Condition,Condition Status,Condition Status,LA9040-2,Ongoing,http://loinc.org".split(
                        ","
                    )
                )
                writer.writerow(
                    "Resolved,Condition has been resolved,Condition,Condition Status,Condition Status,LA9041-0,Resolved,http://loinc.org".split(
                        ","
                    )
                )
                writer.writerow(
                    "History Of,History Of,condition,Condition Status,Condition Status,392521001,Histor of,SMOMED,http://snomed.info/sct".split(
                        ","
                    )
                )

                reader = DictReader(cfile)
                for line in reader:
                    ExtractCoding(line, writer, "HPO Code", "HPO Label", observed_codes)
                    ExtractCoding(
                        line, writer, "MONDO Code", "MONDO Label", observed_codes
                    )
                    ExtractCoding(
                        line, writer, "MAXO Code", "MAXO Label", observed_codes
                    )
                    ExtractCoding(
                        line, writer, "Other Code", "Other Label", observed_codes
                    )
