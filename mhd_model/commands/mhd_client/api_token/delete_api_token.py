import os
import sys
from pathlib import Path

import click

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.mhd_client import MhdAuthClient


@click.command(name="delete", no_args_is_help=True)
@click.option(
    "--api-token",
    help="""API token that will be deleted.""",
    required=True,
)
@click.option(
    "--signed-jwt",
    help="""A valid signed JWT token of the repository.
    It is required if there is no MHD_CLIENT_SIGNED_JWT or
    MHD_CLIENT_SIGNED_JWT_FILE_PATH environment variable.
    """,
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
def delete_api_token_task(
    api_token: str,
    signed_jwt: None | str,
    mhd_server_url: str,
    mhd_server_api_version: str,
):
    """Deletes (invalidates) a MetabolomicsHub API token."""
    if not signed_jwt:
        signed_jwt = os.environ.get("MHD_CLIENT_SIGNED_JWT")
        if not signed_jwt:
            signed_jwt_path = os.environ.get("MHD_CLIENT_SIGNED_JWT_FILE_PATH")
            if not signed_jwt_path or not Path(signed_jwt_path).exists():
                click.echo("Repository signed JWT token is not defined.")
                sys.exit(1)
            signed_jwt = Path(signed_jwt_path).read_text()
    if not mhd_server_url:
        mhd_server_url = os.environ.get("MHD_SERVER_URL")
        if not mhd_server_url:
            mhd_server_url = "https://www.metabolomicshub.org/api/submission"
    if not mhd_server_api_version:
        mhd_server_api_version = os.environ.get("MHD_SERVER_API_VERSION")
        if not mhd_server_api_version:
            mhd_server_api_version = ""

    set_basic_logging_config()
    try:
        client = MhdAuthClient(
            signed_jwt=signed_jwt,
            mhd_webservice_base_url=mhd_server_url,
            api_version=mhd_server_api_version,
        )
        result = client.delete_api_token(api_token=api_token)

        click.echo(f"Message: {result.message}")
        if result.invalidated:
            click.echo("Token deletion status: DELETED")
        else:
            click.echo("Token deletion status: SKIPPED or FAILED")

        return
    except Exception as ex:
        click.echo("API token deletion failed.")
        click.echo(ex)

    exit(1)
