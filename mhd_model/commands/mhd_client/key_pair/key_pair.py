import sys

import click

from mhd_model.commands.mhd_client.key_pair.new_key_pair import new_rsa_key_pair_task
from mhd_model.commands.mhd_client.key_pair.validate_key_pair import (
    validate_rsa_key_pair_task,
)


@click.group(name="key-pair", context_settings={"help_option_names": ["-h", "--help"]})
def key_pair_group():
    """Create and validate public private RSA key pair."""


key_pair_group.add_command(new_rsa_key_pair_task)
key_pair_group.add_command(validate_rsa_key_pair_task)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        key_pair_group(["--help"])
    else:
        key_pair_group()
