#!/usr/bin/env python

from argparse import ArgumentParser, FileType
from pathlib import Path
from csv import reader as Reader
from csv import writer as Writer
from collections import defaultdict

"""Walk through the study file from Pierrette and extract each of the study 
tables and their corresponding contact tables into separate files within the 
correlated table directories.
"""


def run():
    parser = ArgumentParser(
        description="Extract the row associated with each study into their "
        "corresponding table directory"
    )
    parser.add_argument(
        "dataset",
        nargs="+",
        type=FileType("rt", encoding="cp1252"),
        help="The CSV containing all of the study metadata.",
    )
    args = parser.parse_args()

    for study in args.dataset:
        dataset_rows = defaultdict(list)
        reader = Reader(study, delimiter=",", quotechar='"')

        header = None
        contact_data_index = {}

        for line in reader:
            if header is None:
                header = line
            else:
                study_code = line[0]
                destdir = Path("data/tables") / study_code
                destdir.mkdir(parents=True, exist_ok=True)

                dataset_file = destdir / "datasets.csv"

                dataset_rows[dataset_file].append(line)

        for filename in dataset_rows:
            with filename.open("wt") as file:
                writer = Writer(file, delimiter=",", quotechar='"')
                writer.writerow(header)
                for line in dataset_rows[filename]:
                    writer.writerow(line)


if __name__ == "__main__":
    run()
