import sys

import click

from mhd_model import __version__
from mhd_model.commands.create.create import create_group
from mhd_model.commands.validate.validate import validate_group


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__)
def cli():
    """MetabomicsHub CLI with subcommands."""
    pass


cli.add_command(create_group)
cli.add_command(validate_group)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        cli(["--help"])
    else:
        cli()
