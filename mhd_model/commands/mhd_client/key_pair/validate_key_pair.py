import logging
import sys
from pathlib import Path

import click

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.mhd_client_utils import verify_rsa_key_pair

logger = logging.getLogger(__name__)


@click.command(name="validate", no_args_is_help=True)
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
@click.option("--password", help="If exists, password of key pair")
def validate_rsa_key_pair_task(
    private_key_path: str, public_key_path: str, password: None | str
):
    """Validate key pair files."""
    if not Path(private_key_path).exists():
        click.echo(f"{private_key_path} does not exist.")
        sys.exit(1)
    if not Path(public_key_path).exists():
        click.echo(f"{public_key_path} does not exist.")
        sys.exit(1)
    set_basic_logging_config()
    valid = verify_rsa_key_pair(
        private_key_pem=Path(private_key_path).read_bytes(),
        public_key_pem=Path(public_key_path).read_bytes(),
        password=password.encode() if password else None,
    )
    click.echo(f"Public key path:\t{Path(public_key_path).resolve()}")
    click.echo(f"Private key path:\t{Path(private_key_path).resolve()}")
    if valid:
        click.echo("Key pair status:\tVALID")
    else:
        click.echo("Key pair status:\tINVALID")
