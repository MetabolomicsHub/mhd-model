import datetime
import sys
from pathlib import Path

import click

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.mhd_client import MhdAuthClient


@click.command(name="create", no_args_is_help=True)
@click.option(
    "--token-name",
    help="Unique API token name. e.g. prod-2026-02, etc. ",
    required=True,
)
@click.option(
    "--description",
    help="""Description of token usage purpose. e.g. test purpose, etc.""",
)
@click.option(
    "--expiration-time",
    type=datetime.datetime,
    help="""Expiration time of the token. default value is 1 year""",
)
@click.option(
    "--output-file-path",
    help="Output file path to save API token."
    "Resulting API token will be saved in this file if it is set.",
)
@click.pass_context
def create_api_token_task(
    ctx: click.Context,
    token_name: str,
    description: str,
    expiration_time: datetime,
    output_file_path: None | str,
):
    """Creates a new MetabolomicsHub API token.
    The created token will not be shown again. Keep it in secure place and do not share it.
    """
    shared_options = ctx.parent.obj
    mhd_server_url = shared_options["mhd_server_url"]
    mhd_server_api_version = shared_options["mhd_server_api_version"]
    signed_jwt = shared_options["signed_jwt"]

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
