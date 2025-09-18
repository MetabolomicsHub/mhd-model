from __future__ import annotations

import json
from pathlib import Path
from typing import OrderedDict

import click
import jsonschema
from jsonschema import exceptions

from mhd_model.model.v0_1.announcement.validation.base import ProfileValidator
from mhd_model.model.v0_1.announcement.validation.validator import (
    MhdAnnouncementFileValidator,
)
from mhd_model.shared.model import ProfileEnabledDataset
from mhd_model.utils import json_path


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

        number = 0
        profile_validator = ProfileValidator()

        def add_all_leaves(
            err: jsonschema.ValidationError, leaves: list[jsonschema.ValidationError]
        ) -> None:
            if err.validator in profile_validator.validators:
                if not err.context:
                    leaves.append((err.absolute_path, err))
                else:
                    for x in err.context:
                        add_all_leaves(x, leaves)

        errors: OrderedDict = OrderedDict()
        for idx, x in enumerate(all_errors, start=1):
            context_errors = [x]
            if x.validator == "anyOf" and len(x.context) > 1:
                context_errors = [
                    x
                    for x in x.context
                    if x.validator != "type" and x.validator_value != "null"
                ]

            for error_item in context_errors:
                match = exceptions.best_match([error_item])
                error = (json_path(match.absolute_path), match.message)

                if match.validator in profile_validator.validators:
                    leaves = []
                    add_all_leaves(match, leaves)
                    for leaf in leaves:
                        key = json_path(leaf[0])
                        value = leaf[1].message
                        number += 1
                        errors[str(number)] = f"{key}: {value}"
                else:
                    number += 1
                    errors[str(number)] = f"{error[0]}: {error[1]}"
    except Exception as ex:
        errors = {"0": str(ex)}

    errors_list = []
    for idx, x in errors.items():
        errors_list.append(x)

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
