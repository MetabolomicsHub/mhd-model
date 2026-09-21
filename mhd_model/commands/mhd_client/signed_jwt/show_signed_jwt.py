import datetime
import json
import logging
import sys
from pathlib import Path

import click

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.mhd_client_utils import validate_repository_signed_jwt_token

logger = logging.getLogger(__name__)


@click.command(name="show", no_args_is_help=True)
@click.option(
    "--signed-jwt",
    help="""A signed JWT token of the repository.
    """,
)
@click.option(
    "--signed-jwt-file-path",
    help="""A file that contains a signed JWT token of the repository.
    """,
)
@click.option(
    "--audience",
    default="https://www.metabolomicshub.org",
    help="Audience of the JWT token."
    "It MUST be https://www.metabolomicshub.org to use on MetabolomicsHub server",
)
@click.option(
    "--public-key-path",
    help="Public key file path to validate signed JWT. "
    "If it is not defined, validation step will be skipped.",
)
@click.option("--output-file-path", help="Output file path to save JWT token content")
def show_signed_jwt_task(
    signed_jwt: None | str,
    signed_jwt_file_path: None | str,
    audience: str,
    public_key_path: None | str,
    output_file_path: None | str = None,
):
    """Show a signed JWT token content."""
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

    set_basic_logging_config()
    public_key = None
    if public_key_path:
        if not Path(public_key_path).exists():
            click.echo("Public key file path does not exist.")
            sys.exit(1)
        public_key = Path(public_key_path).read_text()

    token, message = validate_repository_signed_jwt_token(
        signed_jwt_token=signed_jwt, audience=audience, public_key=public_key
    )
    token_content = json.dumps(token, indent=2)

    click.echo(message)
    if output_file_path:
        Path(output_file_path).parent.mkdir(exist_ok=True, parents=True)
        Path(output_file_path).write_text(token_content)
        click.echo(f"Signed JWT token content is saved in {output_file_path}")
    click.echo("You can find the signed JWT token content below:\n")
    click.echo(token_content)

    def to_datetime_str(timestamp: int):
        return datetime.datetime.fromtimestamp(timestamp, tz=datetime.UTC).isoformat()

    click.echo("-" * 20)
    click.echo(f"JWT Id:\t\t{token.get('jti', '')}")
    click.echo(f"Issuer:\t\t{token.get('iss', '')}")
    click.echo(f"Subject:\t{token.get('sub', '')}")
    click.echo(f"Audience:\t{token.get('aud', '')}")
    click.echo(f"Created at:\t{to_datetime_str(token.get('iat', ''))}")
    click.echo(f"Valid after:\t{to_datetime_str(token.get('nbf', ''))}")
    click.echo(f"Expires at:\t{to_datetime_str(token.get('exp', ''))}")
