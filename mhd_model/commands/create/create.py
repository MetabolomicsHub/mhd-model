import sys

import click

from mhd_model.commands.create.announcement import create_announcement_file_task
from mhd_model.commands.create.neo4j_input import create_neo4j_input_file_task
from mhd_model.commands.create.sdrf import create_sdrf_file_task


@click.group(name="create", context_settings={"help_option_names": ["-h", "--help"]})
def create_group():
    """utilities to create and convert files (announcement file, etc.)."""
    pass


create_group.add_command(create_announcement_file_task)
create_group.add_command(create_sdrf_file_task)
create_group.add_command(create_neo4j_input_file_task)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        create_group(["--help"])
    else:
        create_group()
