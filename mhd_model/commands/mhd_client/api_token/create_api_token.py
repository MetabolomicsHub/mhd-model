import datetime
import os
import sys
from pathlib import Path

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
    help="""A signed JWT token of the repository.""",
)
@click.option(
    "--signed-jwt-file-path",
    help="""A file that contains a signed JWT token of the repository.""",
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
@click.option("--output-file-path", help="Output file path to save API token")
def create_api_token_task(
    token_name: str,
    signed_jwt: None | str,
    signed_jwt_file_path: None | str,
    description: str,
    expiration_time: datetime,
    output_file_path: None | str,
    mhd_server_url: str,
    mhd_server_api_version: str,
):
    """Creates a new MetabolomicsHub API token.
    The created token will not be shown again. Keep it in secure place and do not share it.
    """
    if not signed_jwt and not signed_jwt_file_path:
        click.echo("Select one of them: signed-jwt, signed-jwt-file-path")
        sys.exit(1)
    if signed_jwt and signed_jwt_file_path:
        click.echo("Select only one of them: signed-jwt, signed-jwt-file-path")
        sys.exit(1)
    if signed_jwt_file_path and not Path(signed_jwt_file_path).exists():
        click.echo(f"{signed_jwt_file_path} does not exist")
        sys.exit(1)
    if signed_jwt_file_path:
        signed_jwt = Path(signed_jwt_file_path).read_text()

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
        repository_token = client.get_new_api_token(
            token_name=token_name,
            expiration_time=expiration_time,
            description=description,
        )

        if output_file_path:
            Path(output_file_path).parent.mkdir(exist_ok=True, parents=True)
            Path(output_file_path).write_text(repository_token.api_token)
            click.echo(f"API key saved in: {output_file_path}")
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

    sys.exit(1)
