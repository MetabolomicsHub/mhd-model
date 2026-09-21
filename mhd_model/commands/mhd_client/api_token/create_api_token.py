import datetime
import os
import sys

import click

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.mhd_client import MhdAuthClient


@click.command(name="create", no_args_is_help=True)
@click.option(
    "--token-name",
    help="""Unique token name. e.g. prod-2026-02, etc. """,
    required=True,
)
@click.option(
    "--signed-jwt",
    help="""A valid signed JWT token of the repository.
    It is required if there is no MHD_CLIENT_SIGNED_JWT environment variable.
    """,
)
@click.option(
    "--description",
    default="",
    help="""Description of token usage purpose. e.g. test purpose, etc.""",
)
@click.option(
    "--expiration-time",
    type=datetime.datetime,
    help="""Expiration time of the token. default value is 1 year""",
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
def create_api_token_task(
    token_name: str,
    signed_jwt: None | str,
    description: str,
    expiration_time: datetime,
    mhd_server_url: str,
    mhd_server_api_version: str,
):
    """Creates a new MetabolomicsHub API token.
    The created token will not be shown again. Keep it in secure place and do not share it.
    """
    if not signed_jwt:
        signed_jwt = os.environ.get("MHD_CLIENT_SIGNED_JWT")
        if not signed_jwt:
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

    set_basic_logging_config()
    try:
        client = MhdAuthClient(
            signed_jwt=signed_jwt,
            mhd_webservice_base_url=mhd_server_url,
            api_version=mhd_server_api_version,
        )
        repository_token = client.get_new_api_token(
            token_name=token_name,
            expiration_time=expiration_time,
            description=description,
        )

        click.echo(f"Message: {repository_token.message}")
        click.echo(f"Token Name: {repository_token.api_token_name}")
        click.echo(f"Expiration time: {repository_token.expiration_time}")
        click.echo(
            "You can find the api-token below. "
            "It will not be shown again, save it in secure place."
        )
        click.echo(repository_token.api_token)
        return
    except Exception as ex:
        click.echo("API token creation failed.")
        click.echo(ex)

    exit(1)
