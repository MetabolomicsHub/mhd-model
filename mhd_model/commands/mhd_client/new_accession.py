from __future__ import annotations

import os
import sys
import traceback
from typing import get_args

import click

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.mhd_client import AccessionType, MhdClient


@click.command(name="fetch-mhd-accession", no_args_is_help=True)
@click.option(
    "--mhd-server-url",
    default="",
    help="MHD Server submission API URL. "
    "It is required if there is no MHD_SERVER_URL environment variable",
)
@click.option(
    "--mhd-server-api-version",
    default="",
    help="Version of MHD Server submission API."
    "Default version will be used if it is not set",
)
@click.option(
    "--accession-type",
    default="mhd",
    help="""MHD accession type.
    Select mhd, legacy, test-legacy, test-mhd, dev
    default is mhd.
    """,
)
@click.option(
    "--api-token",
    default="",
    help="""Repository API token
    It is required if there is no MHD_CLIENT_API_TOKEN environment variable
    """,
)
@click.argument("dataset-repository-identifier")
def get_new_accession_task(
    dataset_repository_identifier: str,
    accession_type: AccessionType,
    mhd_server_url: str,
    mhd_server_api_version: str,
    api_token: str,
):
    """Returns MHD accession number for the repository dataset.
    If dataset has already a MHD accession, MHD server will return the registered accession.
    Otherwise it will create new accession. If accession type is selected as legacy,
    MHD Server will not set an MHD accession and return same repository dataset identifier.
    It returns an output with the specified format REPOSITORY_ACCESSION: MHD_ASSIGNMENT.
    REPOSITORY_ACCESSION: Dataset identifier assigned by repository.
    MHD_ASSIGNMENT: MHD accession for MHD datasets or
    Dataset identifier assigned by repository for legacy datasets
    """
    if not api_token:
        api_token = os.environ.get("MHD_CLIENT_API_TOKEN")
        if not api_token:
            click.echo("Repository API token is not defined.")
            sys.exit(1)
    if not mhd_server_url:
        mhd_server_url = os.environ.get("MHD_SERVER_URL")
        if not mhd_server_url:
            mhd_server_url = "https://www.metabolomicshub.org/api/submission"
    if not mhd_server_api_version:
        mhd_server_api_version = os.environ.get("MHD_SERVER_API_VERSION")
        if not mhd_server_api_version:
            mhd_server_api_version = ""

    if accession_type not in get_args(AccessionType):
        click.echo(f"{accession_type} is not valid. Select valid accession type")
        sys.exit(1)
    set_basic_logging_config()
    try:
        client = MhdClient(
            mhd_webservice_base_url=mhd_server_url,
            api_token=api_token,
            api_version=mhd_server_api_version,
        )
        new_accession = client.get_new_mhd_accession(
            dataset_repository_identifier=dataset_repository_identifier,
            accession_type=accession_type,
        )
        repo_accession = dataset_repository_identifier
        click.echo(f"{repo_accession}: {new_accession}")
    except Exception:
        traceback.print_exc()

    exit(1)
