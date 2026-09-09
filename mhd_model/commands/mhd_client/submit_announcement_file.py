from __future__ import annotations

import sys
import traceback
from pathlib import Path

import click

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.mhd_client import MhdClient


@click.command(name="announce", no_args_is_help=True)
@click.option(
    "--mhd-server-url",
    default="https://www.metabolomicshub.org/api/submission",
    help="MHD Server submission API URL",
)
@click.option(
    "--max-retries",
    default=10,
    type=int,
    help="MHD Server submission API URL",
)
@click.option(
    "--sleep-time",
    default=10,
    type=int,
    help="MHD Server submission API URL",
)
@click.option(
    "--announcement-reason",
    default="Initial submission",
    help="Reason of submission such as initial submission, publication update, etc.",
)
@click.argument("dataset-repository-identifier")
@click.argument("mhd-id")
@click.argument("api-key")
@click.argument("announcement-file-path")
def submit_announcement_file_task(
    dataset_repository_identifier: str,
    mhd_id: str,
    announcement_reason: str,
    api_key: str,
    announcement_file_path: click.Path,
    max_retries: int = 10,
    sleep_time: int = 10,
    mhd_server_url: str = "https://www.metabolomicshub.org/api/submission",
):
    set_basic_logging_config()
    try:
        client = MhdClient(mhd_webservice_base_url=mhd_server_url, api_key=api_key)
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
    except Exception as ex:
        traceback.print_exc()
        click.echo(f"{mhd_id} announcement status: {ex}")
    sys.exit(1)
