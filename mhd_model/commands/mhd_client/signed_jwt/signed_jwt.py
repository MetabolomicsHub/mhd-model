import sys

import click

from mhd_model.commands.mhd_client.signed_jwt.create_signed_jwt import (
    create_signed_jwt_task,
)
from mhd_model.commands.mhd_client.signed_jwt.show_signed_jwt import (
    show_signed_jwt_task,
)


@click.group(
    name="signed-jwt", context_settings={"help_option_names": ["-h", "--help"]}
)
def singed_jwt_group():
    """Create or view repository signed JWT token."""


singed_jwt_group.add_command(create_signed_jwt_task)
singed_jwt_group.add_command(show_signed_jwt_task)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        singed_jwt_group(["--help"])
    else:
        singed_jwt_group()
