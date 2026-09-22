from __future__ import annotations

import json
from pathlib import Path

import click

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.shared.model import ProfileEnabledDataset
from mhd_model.validation import validate_mhd_model


@click.command(name="mhd", no_args_is_help=True)
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
@click.argument("mhd-common-data-file-path")
def validate_mhd_file_task(
    mhd_common_data_file_path: str,
    mhd_id: None | str = None,
    output_file_path: None | str = None,
):
    """Validate MHD model file."""
    set_basic_logging_config()
    if not mhd_id:
        mhd_id = "MHD dataset"
    file = Path(mhd_common_data_file_path)
    try:
        txt = file.read_text()
        announcement_file_json = json.loads(txt)
        profile: ProfileEnabledDataset = ProfileEnabledDataset.model_validate(
            announcement_file_json
        )
        click.echo(
            f"{mhd_id}: {mhd_common_data_file_path} MHD file validation started."
        )
        click.echo(f"Used schema: {profile.schema_name}")
        click.echo(f"Validation profile: {profile.profile_uri}")
        errors_list = validate_mhd_model(mhd_common_data_file_path)

    except Exception as ex:
        import traceback

        traceback.print_exc()
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
            f"{mhd_id}: File '{mhd_common_data_file_path}' is validated successfully."
        )
        exit(0)

    click.echo("")
    click.echo(
        f"{mhd_id}: {mhd_common_data_file_path} has ({len(errors_list)}) validation errors."
    )
    click.echo("-" * 100)
    for idx, item in enumerate(errors_list, start=1):
        click.echo(f"{idx}\t{item}")
    click.echo("-" * 100)
    exit(1)
