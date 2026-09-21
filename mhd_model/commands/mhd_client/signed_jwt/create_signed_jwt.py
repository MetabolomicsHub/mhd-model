import logging
import os
import sys
from pathlib import Path

import click

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.mhd_client_utils import create_signed_jwt

logger = logging.getLogger(__name__)


@click.command(name="create", no_args_is_help=True)
@click.option(
    "--repository-name",
    help="Repository name. It is case sensitive and "
    "MUST be exactly match the one specified in MetabolomicsHub database. "
    "It is required if there is no MHD_REPOSITORY_NAME environment variable.",
    required=True,
)
@click.option(
    "--private-key-path",
    help="Private key file path",
    required=True,
)
@click.option(
    "--public-key-path",
    help="Public key file path",
    required=True,
)
@click.option(
    "--validity-period-in-days",
    type=int,
    default=365 * 3,
    help="Validity period in days. Default is 365 * 3 days",
)
@click.option(
    "--audience",
    default="https://www.metabolomicshub.org",
    help="Audience of the JWT token."
    "It MUST be https://www.metabolomicshub.org to use on MetabolomicsHub server",
)
@click.option("--output-file-path", help="Output file path to save signed JWT token.")
def create_signed_jwt_task(
    repository_name: str,
    private_key_path: str,
    public_key_path: str,
    output_file_path: None | str = None,
    validity_period_in_days: int = 365 * 3,
    audience: str = "https://www.metabolomicshub.org",
):
    """Create signed JWT token to create MetabolomicsHub API tokens."""
    if not repository_name:
        repository_name = os.environ.get("MHD_REPOSITORY_NAME")
        if not repository_name:
            click.echo("repository name is not valid.")
            sys.exit(1)
    if validity_period_in_days < 1:
        click.echo("validity-period-in-days parameter is not valid.")
        sys.exit(1)
    if not Path(private_key_path).exists():
        click.echo(f"{private_key_path} does not exist.")
        sys.exit(1)
    if not Path(public_key_path).exists():
        click.echo(f"{public_key_path} does not exist.")
        sys.exit(1)

    set_basic_logging_config()
    token = create_signed_jwt(
        repository_name=repository_name,
        private_key_path=Path(private_key_path),
        public_key_path=Path(public_key_path),
        signed_jwt_token_path=Path(output_file_path) if output_file_path else None,
        validity_period_in_days=validity_period_in_days,
        audience=audience,
    )

    click.echo("You can find the signed JWT below:\n")
    click.echo(token)
