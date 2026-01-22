from __future__ import annotations

import json
from pathlib import Path

import click

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.model.v0_1.announcement.validation.validator import (
    MhdAnnouncementFileValidator,
)
from mhd_model.shared.model import ProfileEnabledDataset


@click.command(name="announcement", no_args_is_help=True)
@click.option(
    "--output-path",
    default=None,
    help="Validation output file path",
)
@click.argument("mhd_study_id")
@click.argument("announcement_file_path")
def validate_announcement_file_task(
    mhd_study_id: str,
    announcement_file_path: str,
    output_path: None | str,
):
    """Validate MHD announcement file.

    Args:

    mhd_study_id (str): MHD study id

    announcement_file_path (str): MHD announcement file path

    output_path (None | str): If it is defined, validation results are saved in output file path.
    """
    set_basic_logging_config()
    file = Path(announcement_file_path)
    try:
        txt = file.read_text()
        announcement_file_json = json.loads(txt)
        profile: ProfileEnabledDataset = ProfileEnabledDataset.model_validate(
            announcement_file_json
        )
        click.echo(f"Used schema: {profile.schema_name}")
        click.echo(f"Validation profile: {profile.profile_uri}")

        validator = MhdAnnouncementFileValidator()
        all_errors = validator.validate(announcement_file_json)

    except Exception as ex:
        all_errors.append(str(ex))

    errors_list = all_errors

    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w") as f:
            result = {
                "success": len(errors_list) == 0,
                "errors": [str(x) for x in errors_list],
            }
            json.dump(result, f, indent=4)
    if not errors_list:
        click.echo(
            f"{mhd_study_id}: File '{announcement_file_path}' is validated successfully."
        )
        exit(0)
    click.echo(f"{mhd_study_id}: {announcement_file_path} has validation errors.")
    for idx, error in enumerate(errors_list, start=1):
        click.echo(f"{idx}: {error}")

    exit(1)
