import sys

import click

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.mhd_client import MhdAuthClient


@click.command(name="validate", no_args_is_help=True)
@click.option(
    "--api-token",
    help="""API token that will be validated""",
    required=True,
)
@click.pass_context
def validate_api_token_task(
    ctx: click.Context,
    api_token: str,
    signed_jwt: None | str,
):
    """Validated a MetabolomicsHub API token."""
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
        result = client.validate_api_token(api_token=api_token)

        click.echo(f"Message: {result.message}")
        if result.valid:
            click.echo("Validation status: VALID")
        else:
            click.echo("Validation status: INVALID")
        return
    except Exception as ex:
        click.echo("API token creation failed.")
        click.echo(ex)

    sys.exit(1)
