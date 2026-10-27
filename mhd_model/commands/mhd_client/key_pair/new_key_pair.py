from pathlib import Path

import click

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.mhd_client_utils import generate_rsa_key_pair


@click.command(name="create", no_args_is_help=False)
@click.option(
    "--output-folder",
    default=".",
    help="Output folder",
)
@click.option(
    "--key-size", default=4096, type=int, help="Key size of the generated RSA keys."
)
def new_rsa_key_pair_task(
    output_folder: str,
    key_size: int,
):
    """Generate RSA public private key pair to create signed JWT tokens.
    Public key file MUST be shared with MetabolomicsHub.
    Repositories can create MetabolomicsHub API tokens using signed JWT tokens.
    """
    set_basic_logging_config()
    output_folder = Path(output_folder).resolve()
    private_pem, public_pem = generate_rsa_key_pair(key_size=key_size)
    Path(output_folder).mkdir(exist_ok=True, parents=True)
    private_key_path = Path(f"{output_folder}/private_key.pem")
    private_key_path.write_bytes(private_pem)
    private_key_path.chmod(0o600)

    public_key_path = Path(f"{output_folder}/public_key.pem")
    public_key_path.write_bytes(public_pem)
    click.echo(f"RSA key pairs are saved to {output_folder}")

    click.echo(f"Private key file: {private_key_path}")
    click.echo(
        "Do not send private key file to MetabolomicsHub. "
        "Do not share private key file with anyone!"
    )

    click.echo(f"Public key: {public_key_path}")
    click.echo(
        "If you want to use new key pair, "
        "share public key file with MetabolomicsHub, "
        "create signed JWT token to create new api tokens."
    )
