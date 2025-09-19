from __future__ import annotations

import json
from pathlib import Path

import click

from mhd_model.model.v0_1.dataset.validation.validator import validate_mhd_file
from mhd_model.shared.model import ProfileEnabledDataset


@click.command(name="mhd", no_args_is_help=True)
@click.option(
    "--output-path",
    default=None,
    help="Validation output file path",
)
@click.argument("mhd_study_id")
@click.argument("mhd_model_file_path")
def validate_mhd_file_task(
    mhd_study_id: str,
    mhd_model_file_path: str,
    output_path: None | str,
):
    """Validate MHD model file.

    Args:

    mhd_study_id (str): MHD study id

    mhd_model_file_path (str): MHD model file path

    output_path (None | str): If it is not None, validation results are saved in output file path.
    """
    file = Path(mhd_model_file_path)
    try:
        txt = file.read_text()
        announcement_file_json = json.loads(txt)
        profile: ProfileEnabledDataset = ProfileEnabledDataset.model_validate(
            announcement_file_json
        )
        click.echo(
            f"{mhd_study_id}: {mhd_model_file_path} MHD file validation started."
        )
        click.echo(f"Used schema: {profile.schema_name}")
        click.echo(f"Validation profile: {profile.profile_uri}")
        all_errors = validate_mhd_file(mhd_model_file_path)

    except Exception as ex:
        import traceback

        traceback.print_exc()
        all_errors = [("exception", str(ex))]

    errors_list = []
    for key, error in all_errors:
        if hasattr(error, "message"):
            errors_list.append({"key": key, "error": error.message})
        else:
            errors_list.append({"key": key, "error": error})

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
            f"{mhd_study_id}: File '{mhd_model_file_path}' is validated successfully."
        )
        exit(0)

    click.echo("")
    click.echo(
        f"{mhd_study_id}: {mhd_model_file_path} has ({len(errors_list)}) validation errors."
    )
    click.echo("-" * 100)
    for idx, item in enumerate(errors_list, start=1):
        click.echo(f"{idx}\t{item.get('key')}\t{item.get('error')}")
    click.echo("-" * 100)
    exit(1)
