import json
from pathlib import Path

import click

from mhd_model.convertors.announcement.convertor import create_announcement_file
from mhd_model.log_utils import set_basic_logging_config


@click.command(name="announcement", no_args_is_help=True)
@click.option(
    "--output-dir",
    default="outputs",
    show_default=True,
    help="Output directory for MHD file",
)
@click.option(
    "--output-filename",
    default=None,
    show_default=True,
    help="MHD announcement filename (e.g., MHD000001.announcement.json, ST000001.announcement.json)",
)
@click.option("--mhd-id", help="MHD Id")
@click.option(
    "--mhd-common-data-file-path", help="MHD common data filepath", required=True
)
@click.option(
    "--target-mhd-common-data-file-url",
    help="Target URL of MHD common data file. "
    "If announcement file is shared with MetabolomicsHub, "
    "MetabolomicsHub will check the URL for accessibility",
    required=True,
)
def create_announcement_file_task(
    mhd_id: None | str,
    mhd_common_data_file_path: str,
    target_mhd_common_data_file_url: str,
    output_dir: str,
    output_filename: None | str,
):
    """Create announcement file from MHD data model file."""
    set_basic_logging_config()
    file = Path(mhd_common_data_file_path)
    txt = file.read_text()
    mhd_data_json = json.loads(txt)

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    announcement_file_path = f"{output_dir}/{mhd_id}.announcement.json"
    if output_filename:
        announcement_file_path = f"{output_dir}/{output_filename}"
    try:
        create_announcement_file(
            mhd_data_json, target_mhd_common_data_file_url, announcement_file_path
        )
        click.echo(f"{mhd_id} announcement file conversion completed.")
    except Exception as ex:
        click.echo(f"{mhd_id} announcement file conversion failed. {ex!s}")
