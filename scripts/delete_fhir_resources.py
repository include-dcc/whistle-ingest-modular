#!/usr/bin/env python

from argparse import ArgumentParser, FileType
import sys
from ncpi_fhir_client.fhir_client import FhirClient
from ncpi_fhir_client.host_config import get_host_config

from wstlr.hostfile import load_hosts_file
from collections import defaultdict
from pathlib import Path
from rich import print
import pdb
import yaml

"""
Just a simple script that allows you to delete resources by ID using a YAML 
file with keys as resource types pointing to a list of IDs
"""


def exec(args=None):
    if args is None:
        args = sys.argv[1:]

    host_config = load_hosts_file("fhir_hosts")
    # Just capture the available environments to let the user
    # make the selection at runtime
    env_options = sorted(host_config.keys())

    parser = ArgumentParser(description="Delete FHIR resources by ID")
    parser.add_argument(
        "-e",
        "--env",
        choices=env_options,
        required=True,
        help=f"Remote configuration to be used to access the FHIR server. If no environment is provided, the system will stop after generating the whistle output (no validation, no loading)",
    )
    parser.add_argument(
        "-r",
        "--resource-type",
        choices=["Patient", "Condition", "Observation"],
        help="The resource type of the resources to be deleted",
    )
    parser.add_argument(
        "id",
        nargs="+",
        help="Which IDs are to be deleted (must be of type, --resource-type)",
    )
    args = parser.parse_args(args)

    fhir_client = FhirClient(host_config[args.env])
    for id in args.id:
        result = fhir_client.delete_by_record_id(args.resource_type, id)
        print(f"DELETE {id} -> {result['status_code']}")


if __name__ == "__main__":
    exec()
