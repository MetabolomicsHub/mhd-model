import logging
import sys
from pathlib import Path

import click
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from mhd_model.log_utils import set_basic_logging_config

logger = logging.getLogger(__name__)


def verify_rsa_key_pair(
    private_key_pem: bytes, public_key_pem: bytes, password: None | bytes = None
) -> bool:
    """
    Verifies that a given PEM-encoded RSA private key and public key are valid and match.

    :param private_key_pem: The private key in PEM format (bytes).
    :param public_key_pem: The public key in PEM format (bytes).
    :param password: Password for the private key if encrypted, otherwise None.
    :return: True if the keys are valid and form a matching pair, False otherwise.
    """
    try:
        # 1. Load the private key (this validates the private key structure)
        private_key = serialization.load_pem_private_key(
            private_key_pem, password=password
        )

        # Ensure it's actually an RSA key
        if not isinstance(private_key, rsa.RSAPrivateKey):
            logger.error("Private key is not an RSA key.")
            return False

        # 2. Load the public key (this validates the public key structure)
        public_key = serialization.load_pem_public_key(public_key_pem)

        if not isinstance(public_key, rsa.RSAPublicKey):
            logger.error("Public key is not an RSA key.")
            return False

        # 3. Compare the public numbers (modulus 'n' and public exponent 'e')
        # A private key inherently contains its corresponding public key mathematically.
        derived_public_numbers = private_key.public_key().public_numbers()
        provided_public_numbers = public_key.public_numbers()

        if derived_public_numbers == provided_public_numbers:
            return True
        else:
            logger.error("The public key does not match the private key.")
            return False

    except ValueError as e:
        logger.error("Key parsing error (incorrect password or bad format): %s", e)
        return False
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
        return False


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
