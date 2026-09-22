from __future__ import annotations

import json
from pathlib import Path

import click

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.validation import validate_announcement_file


@click.command(name="announcement", no_args_is_help=True)
@click.option(
    "--mhd-id",
    default=None,
    help="MHD Accession of dataset.",
)
@click.option(
    "--output-file-path",
    default=None,
    help="Validation output file path",
)
@click.argument("announcement-file-path")
def validate_announcement_file_task(
    announcement_file_path: str,
    mhd_id: None | str = None,
    output_file_path: None | str = None,
):
    """Validate MHD announcement file."""
    set_basic_logging_config()
    if not mhd_id:
        mhd_id = "MHD Announcement File"
    try:
        errors_list = validate_announcement_file(announcement_file_path)

    except Exception as ex:
        errors_list = [str(ex)]

    if output_file_path:
        output_file = Path(output_file_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w") as f:
            result = {
                "success": len(errors_list) == 0,
                "errors": [str(x) for x in errors_list],
            }
            json.dump(result, f, indent=4)
    if not errors_list:
        click.echo(
            f"{mhd_id}: File '{announcement_file_path}' is validated successfully."
        )
        exit(0)
    click.echo(f"{mhd_id}: {announcement_file_path} has validation errors.")
    for idx, error in enumerate(errors_list, start=1):
        click.echo(f"{idx}: {error}")

    exit(1)
