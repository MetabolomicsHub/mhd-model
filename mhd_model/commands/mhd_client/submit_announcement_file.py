from __future__ import annotations

import os
import sys
from pathlib import Path

import click

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.mhd_client import MhdClient, MhdClientError


@click.command(name="announce", no_args_is_help=True)
@click.option(
    "--announcement-reason",
    default="Initial submission",
    required=True,
    help="Reason of submission such as initial submission, publication update, etc.",
)
@click.option(
    "--mhd-id",
    required=True,
    help="MHD accession number for MHD dataset otherwise repository dataset identifier",
)
@click.option(
    "--announcement-file-path",
    required=True,
    help="Announcement file path",
)
@click.option(
    "--mhd-server-url",
    default="",
    help="MHD Server submission API URL",
)
@click.option(
    "--mhd-server-api-version",
    default="",
    help="Version of MHD Server submission API."
    "Default version will be used if it is not set",
)
@click.option(
    "--max-retries",
    default=20,
    type=int,
    help="MHD Server submission API URL",
)
@click.option(
    "--sleep-time",
    default=15,
    type=int,
    help="MHD Server submission API URL",
)
@click.option(
    "--api-token",
    default="",
    help="""Repository API token""",
)
@click.option(
    "--api-token-file-path",
    default="",
    help="""Repository API token file path
    """,
)
@click.option(
    "--dataset-repository-identifier",
    default="",
    help="""Dataset Identifier managed by repository
    """,
    required=True,
)
def submit_announcement_file_task(
    dataset_repository_identifier: str,
    mhd_id: str,
    announcement_reason: str,
    api_token: None | str,
    api_token_file_path: None | str,
    announcement_file_path: click.Path,
    mhd_server_url: str,
    mhd_server_api_version: str,
    max_retries: int = 10,
    sleep_time: int = 10,
):
    """Send MHD announcement file to MetabolomicsHub server.
    It sends the file and waits its validation. If the submission is successful,
    it prints submission status (VALID) otherwise prints FAILED
    """
    set_basic_logging_config()
    if not api_token:
        if api_token_file_path and Path(api_token_file_path).exists():
            api_token = Path(api_token_file_path).read_text().strip()
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
    try:
        client = MhdClient(
            mhd_webservice_base_url=mhd_server_url,
            api_token=api_token,
            api_version=mhd_server_api_version,
        )
        if not Path(announcement_file_path).exists():
            click.echo(f"{announcement_file_path} does not exist")
            sys.exit(1)

        click.echo(f"{announcement_file_path} will be uploaded")
        submitted_revision = client.submit_announcement_file(
            dataset_repository_id=dataset_repository_identifier,
            mhd_id=mhd_id,
            announcement_reason=announcement_reason,
            max_retries=max_retries,
            sleep_time=sleep_time,
            file_path=announcement_file_path,
        )
        click.echo(f"{mhd_id} announcement status: {submitted_revision.status}")
        return
    except Exception as ex:
        if isinstance(ex, MhdClientError):
            click.echo(ex.message)
        else:
            click.echo(str(ex))

        click.echo(f"{mhd_id} announcement status: FAILED")

    sys.exit(1)
