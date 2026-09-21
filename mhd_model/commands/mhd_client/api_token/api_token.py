import sys

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


@click.group(name="api-token", context_settings={"help_option_names": ["-h", "--help"]})
def api_token_group():
    """Create and maintain MetabolomicsHub API token."""


api_token_group.add_command(create_api_token_task)
api_token_group.add_command(validate_api_token_task)
api_token_group.add_command(list_api_tokens_task)
api_token_group.add_command(delete_api_token_task)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        api_token_group(["--help"])
    else:
        api_token_group()
