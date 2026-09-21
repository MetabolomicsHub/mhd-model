import sys

import click

from mhd_model.commands.mhd_client.api_token.api_token import api_token_group
from mhd_model.commands.mhd_client.key_pair.key_pair import key_pair_group
from mhd_model.commands.mhd_client.new_accession import get_new_accession_task
from mhd_model.commands.mhd_client.signed_jwt.signed_jwt import singed_jwt_group
from mhd_model.commands.mhd_client.submit_announcement_file import (
    submit_announcement_file_task,
)


@click.group(name="client", context_settings={"help_option_names": ["-h", "--help"]})
def mhd_client_group():
    """utilities to communicate with MHD Server."""


mhd_client_group.add_command(get_new_accession_task)
mhd_client_group.add_command(submit_announcement_file_task)
mhd_client_group.add_command(key_pair_group)
mhd_client_group.add_command(singed_jwt_group)
mhd_client_group.add_command(api_token_group)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        mhd_client_group(["--help"])
    else:
        mhd_client_group()
