import json
from pathlib import Path

import click

from mhd_model.convertors.announcement.v0_1.legacy.mhd2announce import (
    create_announcement_file,
)


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
@click.argument("mhd_study_id")
@click.argument("mhd_model_file_path")
@click.argument("target_mhd_model_file_url")
def create_announcement_file_task(
    mhd_study_id: str,
    mhd_model_file_path: str,
    target_mhd_model_file_url: str,
    output_dir: str,
    output_filename: str,
):
    """Create announcement file from MHD data model file.

    Args:

    mhd_study_id (str): MHD study identifier

    mhd_model_file_path (str): MHD data model path

    target_mhd_model_file_url (str): target URL of MHD data model

    output_dir (str): Output directory of announcement file

    output_filename (str): Name of MHD announcement file. Default is <repository identifier>.announcement.json
    """
    file = Path(mhd_model_file_path)
    txt = file.read_text()
    mhd_data_json = json.loads(txt)

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    announcement_file_path = f"{output_dir}/{mhd_study_id}.announcement.json"
    if output_filename:
        announcement_file_path = f"{output_dir}/{output_filename}"
    try:
        create_announcement_file(
            mhd_data_json, target_mhd_model_file_url, announcement_file_path
        )
        click.echo(f"{mhd_study_id} announcement file conversion completed.")
    except Exception as ex:
        click.echo(f"{mhd_study_id} announcement file conversion failed. {str(ex)}")
