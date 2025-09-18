import sys

import click

from mhd_model.commands.validate.announcement import validate_announcement_file_task
from mhd_model.commands.validate.mhd_file import validate_mhd_file_task


@click.group(name="validate", context_settings={"help_option_names": ["-h", "--help"]})
def validate_group():
    """utilities to validate MetabolomicsHub files."""
    pass


validate_group.add_command(validate_announcement_file_task)
validate_group.add_command(validate_mhd_file_task)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        validate_group(["--help"])
    else:
        validate_group()
