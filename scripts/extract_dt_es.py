#!/usr/bin/env python

from csv import DictReader, writer as csv_writer
from collections import defaultdict
from yaml import safe_load
from argparse import ArgumentParser, FileType

import pdb

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

    data_types = set()
    experimental_strategies = set()

    # First, let's grab the datafile harmony file so that we can exclude anything that
    # is already there
    already_in_harmony = defaultdict(set)
    with open("harmony/datafile.csv", 'rt') as inf:
        reader = DictReader(inf)
        for line in reader:
            already_in_harmony[line['local code system']].add(line['local code'])


    for f in args.config:
        config = safe_load(f)

        study_id = config["study_id"]

        for filename in config["dataset"]["file_manifest"]["filename"].split(","):
            with open(filename, "rt") as dfile:
                reader = DictReader(dfile)
                for line in reader:
                    dt = line.get("Data Type")
                    if dt and dt.strip() != "":
                        data_types.add(dt)
                    es = line.get("Experimental Strategy")
                    if es and es.strip() != "":
                        experimental_strategies.add(es)

        output_filename = args.output
        if output_filename is None:
            output_filename = f"harmony/data_types_and_experimental_strategies.csv"

        with open(output_filename, 'wt') as outf:
            writer = csv_writer(outf)
            writer.writerow(
                "local code,text,table_name,parent_varname,local code system,code,display,code system,comment".split(
                    ","
                )
            )

            exp_skipped = 0
            exp_new = 0
            for exp_strategy in sorted(list(experimental_strategies)):
                if exp_strategy not in already_in_harmony['Experimental Strategy']:
                    # harmonized_terms = [exp_strategy]
                    harmonized_terms = exp_strategy.split("|")
                    for ht in harmonized_terms:
                        writer.writerow([
                            exp_strategy,
                            exp_strategy,
                            "datafile",
                            "Experimental Strategy",
                            "Experimental Strategy",
                            ht,
                            ht,
                            "https://includedcc.org/fhir/code-systems/experimental_strategies"
                        ])
                    exp_new += 1
                else:
                    exp_skipped += 1
            
            dt_skipped = 0 
            dt_new = 0
            
            for dtype in sorted(list(data_types)):
                if dtype not in already_in_harmony['Data Type']:
                    harmonized_terms = [dtype]
                    # harmonized_terms = dtype.split("|")
                    for ht in harmonized_terms:
                        writer.writerow([
                            dtype,
                            dtype, 
                            "datafile",
                            "Data Type",
                            "Data Type",
                            ht,
                            ht,
                            "https://includedcc.org/fhir/code-systems/data_types"
                        ])
                    dt_new += 1 
                else:
                    dt_skipped +=1 
        
        print(f"Job completed. New Harmony file: {output_filename}")
        print(f"    Experimental Strategy: {exp_new} new   {exp_skipped} already present in datafile harmony")
        print(f"    Data Type            : {dt_new} new   {dt_skipped} already present in datafile harmony")

