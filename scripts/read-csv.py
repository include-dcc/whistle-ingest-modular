#!/usr/bin/env python

"""This is just a quick way to review a CSV file in JSONish format so that I can avoid Excel. It will just dump the output from DictReader to stdout..."""

from csv import DictReader
import sys
from rich import print
import os
from argparse import ArgumentParser, FileType

import pdb

if __name__ == "__main__":
    parser = ArgumentParser(
        description="Quickly dump some or all of a CSV file in a JSON like, readable format."
    )

    parser.add_argument(
        "file", nargs="+", type=FileType("rt"), help="CSV file to be inspected. "
    )

    parser.add_argument("-i", "--index", type=int, action="append")
    parser.add_argument("-c", "--row-count", type=int, default=-1)
    args = parser.parse_args()

    if args.index is None or len(args.index) == 0:
        # We'll assume no index means just start at the beginning
        args.index = set([1])
    else:
        args.index = set(args.index)

    for file in args.file:
        try:
            reader = DictReader(file)

            rows_shown = 0
            row_count = 1
            row_index = 1

            for row in reader:
                row_index += 1
                if row_index in args.index:
                    row_count = args.row_count
                    rows_shown = 0
                if row_count < 1 or rows_shown < row_count:
                    print(row)
                    rows_shown += 1
        except:
            os.system(f"file --mime-encoding {file.name}")
            print()
            print(f"There was a problem reading the file, {file.name}")
