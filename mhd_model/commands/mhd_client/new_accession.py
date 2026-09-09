from __future__ import annotations

import sys
import traceback
from typing import get_args

import click

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.mhd_client import AccessionType, MhdClient


@click.command(name="fetch-mhd-accession", no_args_is_help=True)
@click.option(
    "--mhd-server-url",
    default="https://www.metabolomicshub.org/api/submission",
    help="MHD Server submission API URL",
)
@click.option(
    "--accession-type",
    default="mhd",
    help="""MHD accession type.
    Select mhd, legacy, test-legacy, test-mhd, dev
    default is mhd.
    """,
)
@click.argument("dataset-repository-identifier")
@click.argument("api-key")
def get_new_accession_task(
    dataset_repository_identifier: str,
    mhd_server_url: str,
    accession_type: AccessionType,
    api_key: str,
):
    if accession_type not in get_args(AccessionType):
        click.echo(f"{accession_type} is not valid. Select valid accession type")
        sys.exit(1)
    set_basic_logging_config()
    try:
        client = MhdClient(mhd_webservice_base_url=mhd_server_url, api_key=api_key)
        new_accession = client.get_new_mhd_accession(
            dataset_repository_identifier=dataset_repository_identifier,
            accession_type=accession_type,
        )
        repo_accession = dataset_repository_identifier
        click.echo(f"MHD Accession for {repo_accession}: {new_accession}")
    except Exception:
        traceback.print_exc()

    exit(1)
