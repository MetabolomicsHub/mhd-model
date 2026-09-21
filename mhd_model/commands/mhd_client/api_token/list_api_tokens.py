import os
import sys
from pathlib import Path

import click

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.mhd_client import MhdAuthClient


@click.command(name="list", no_args_is_help=True)
@click.option(
    "--token-name",
    help="""Unique token name to filter API tokens. e.g. prod-2026-02, etc. """,
)
@click.option(
    "--include-invalid-api-tokens",
    help="""If it is set, response includes invalid tokens in response""",
    is_flag=True,
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
def list_api_tokens_task(
    token_name: None | str,
    include_invalid_api_tokens: None | bool,
    signed_jwt: None | str,
    mhd_server_url: str,
    mhd_server_api_version: str,
):
    """Lists the created MetabolomicsHub API tokens' summary.
    MetabolomicsHub stores only hash value and summary of a API token.
    Result will how only summary of API tokens.
    """
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
        tokens = client.list_api_tokens(
            token_name=token_name, include_invalid_api_tokens=include_invalid_api_tokens
        )
        for idx, token in enumerate(tokens, start=1):
            click.echo(f"API Token: {idx}")
            click.echo(f"Name: {token.name}")
            if token.description:
                click.echo(f"Description: {token.description}")
            click.echo(f"Created at: {token.modified_at}")
            click.echo(f"Expiration date: {token.expiration_datetime}")
            if token.modified_at:
                click.echo(f"Modified: {token.modified_at}")
            click.echo("-" * 20)
            return
    except Exception as ex:
        click.echo("API token creation failed.")
        click.echo(ex)

    exit(1)
