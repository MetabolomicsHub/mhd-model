import os
import sys
from pathlib import Path

import click

from mhd_model.commands.mhd_client.api_token.create_api_token import (
    create_api_token_task,
)
from mhd_model.commands.mhd_client.api_token.delete_api_token import (
    delete_api_token_task,
)
from mhd_model.commands.mhd_client.api_token.list_api_tokens import list_api_tokens_task
from mhd_model.commands.mhd_client.api_token.validate_api_token import (
    validate_api_token_task,
)
from mhd_model.mhd_client_utils import create_signed_jwt


@click.group(name="api-token", context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--repository-name",
    help="Repository name used to create a signed JWT. "
    "MHD_REPOSITORY_NAME is used when omitted.",
)
@click.option(
    "--private-key-path",
    help="Private key file path. MHD_REPOSITORY_PRIVATE_KEY_PATH is used when omitted.",
)
@click.option(
    "--public-key-path",
    help="Public key file path. MHD_REPOSITORY_PUBLIC_KEY_PATH is used when omitted.",
)
@click.option(
    "--audience",
    default=None,
    help="Audience of the JWT token. MHD_AUDIENCE is used when omitted.",
)
@click.pass_context
def api_token_group(
    ctx: click.Context,
    repository_name: str | None,
    private_key_path: str | None,
    public_key_path: str | None,
    audience: str | None,
):
    """Create and maintain MetabolomicsHub API token."""

    if not private_key_path:
        private_key_path = os.environ.get("MHD_REPOSITORY_PRIVATE_KEY_PATH")
    if not private_key_path or not Path(private_key_path).exists():
        click.echo("Repository private key path is not defined or does not exist.")
        sys.exit(1)
    if not public_key_path:
        public_key_path = os.environ.get("MHD_REPOSITORY_PUBLIC_KEY_PATH")
    if not public_key_path or not Path(public_key_path).exists():
        click.echo("Repository public key path is not defined or does not exist.")
        sys.exit(1)
    if not repository_name:
        repository_name = os.environ.get("MHD_REPOSITORY_NAME")
    if not repository_name:
        click.echo("repository name is not valid.")
        sys.exit(1)
    if not audience:
        audience = os.environ.get("MHD_AUDIENCE")
    if not audience:
        audience = "https://www.metabolomicshub.org"
        click.echo(f"Using default audience: {audience}")
    if ctx.parent and ctx.parent.obj:
        client_options = ctx.parent.obj
    else:
        client_options = {
            "mhd_server_url": os.environ.get("MHD_SERVER_URL")
            or "https://www.metabolomicshub.org/api/submission",
            "mhd_server_api_version": os.environ.get("MHD_SERVER_API_VERSION") or "",
        }

    signed_jwt = create_signed_jwt(
        repository_name=repository_name,
        private_key_path=Path(private_key_path),
        public_key_path=Path(public_key_path),
        validity_period_in_mins=1,
        audience=audience,
    )
    ctx.obj = {
        "repository_name": repository_name,
        "private_key_path": private_key_path,
        "public_key_path": public_key_path,
        "audience": audience,
        "mhd_server_url": client_options["mhd_server_url"],
        "mhd_server_api_version": client_options["mhd_server_api_version"],
        "signed_jwt": signed_jwt,
    }


api_token_group.add_command(create_api_token_task)
api_token_group.add_command(validate_api_token_task)
api_token_group.add_command(list_api_tokens_task)
api_token_group.add_command(delete_api_token_task)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        api_token_group(["--help"])
    else:
        api_token_group()
