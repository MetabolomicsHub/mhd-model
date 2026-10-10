import json
import logging
import pathlib

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.model.v1_0.announcement.profiles.base_profile import (
    BASE_ANNOUNCEMENT_FILE_PROFILE_v1_0,
)
from mhd_model.model.v1_0.announcement.profiles.legacy_profile import (
    LEGACY_ANNOUNCEMENT_FILE_PROFILE_v1_0,
)
from mhd_model.model.v1_0.announcement.profiles.ms_profile import (
    MS_ANNOUNCEMENT_FILE_PROFILE_v1_0,
)
from mhd_model.model.v1_0.announcement.profiles.profile import AnnouncementBaseProfile
from mhd_model.model.v1_0.dataset.profiles.base import profile as v1_0_mhd_base_profile
from mhd_model.model.v1_0.dataset.profiles.legacy import (
    profile as v1_0_mhd_legacy_profile,
)
from mhd_model.model.v1_0.dataset.profiles.ms import profile as v1_0_mhd_ms_profile

logger = logging.getLogger(__name__)


def update_schema_files() -> None:
    models = [
        (
            AnnouncementBaseProfile,
            "v0_1",
            "announcement-v0.1.schema.json",
        ),
        (
            BASE_ANNOUNCEMENT_FILE_PROFILE_v1_0.model_dump(
                by_alias=True, exclude_none=True, serialize_as_any=True
            ),
            "v0_1",
            "announcement-v0.1.base-profile.json",
        ),
        (
            LEGACY_ANNOUNCEMENT_FILE_PROFILE_v1_0.model_dump(
                by_alias=True, exclude_none=True, serialize_as_any=True
            ),
            "v0_1",
            "announcement-v0.1.legacy-profile.json",
        ),
        (
            MS_ANNOUNCEMENT_FILE_PROFILE_v1_0.model_dump(
                by_alias=True, exclude_none=True, serialize_as_any=True
            ),
            "v0_1",
            "announcement-v0.1.ms-profile.json",
        ),
        (
            v1_0_mhd_base_profile.MhDatasetBaseProfile_v1_0,
            "v0_1",
            "common-data-model-v0.1.schema.json",
        ),
        (
            v1_0_mhd_legacy_profile.MhDatasetLegacyProfile_v1_0,
            "v0_1",
            "common-data-model-v0.1.legacy-profile.json",
        ),
        (
            v1_0_mhd_ms_profile.MhDatasetBaseProfile_v1_0,
            "v0_1",
            "common-data-model-v0.1.ms-profile.json",
        ),
        (
            AnnouncementBaseProfile,
            "v1_0",
            "announcement-v1.0.schema.json",
        ),
        (
            BASE_ANNOUNCEMENT_FILE_PROFILE_v1_0.model_dump(
                by_alias=True, exclude_none=True, serialize_as_any=True
            ),
            "v1_0",
            "announcement-v1.0.base-profile.json",
        ),
        (
            LEGACY_ANNOUNCEMENT_FILE_PROFILE_v1_0.model_dump(
                by_alias=True, exclude_none=True, serialize_as_any=True
            ),
            "v1_0",
            "announcement-v1.0.legacy-profile.json",
        ),
        (
            MS_ANNOUNCEMENT_FILE_PROFILE_v1_0.model_dump(
                by_alias=True, exclude_none=True, serialize_as_any=True
            ),
            "v1_0",
            "announcement-v1.0.ms-profile.json",
        ),
        (
            v1_0_mhd_base_profile.MhDatasetBaseProfile_v1_0,
            "v1_0",
            "common-data-model-v1.0.schema.json",
        ),
        (
            v1_0_mhd_legacy_profile.MhDatasetLegacyProfile_v1_0,
            "v1_0",
            "common-data-model-v1.0.legacy-profile.json",
        ),
        (
            v1_0_mhd_ms_profile.MhDatasetMsProfile_v1_0,
            "v1_0",
            "common-data-model-v1.0.ms-profile.json",
        ),
    ]
    schema_path = pathlib.Path("mhd_model/schemas/mhd")
    schema_path.mkdir(parents=True, exist_ok=True)
    for model_class, version, filename in models:
        docs_path = pathlib.Path(f"docs/schemas/{version}")
        docs_path.mkdir(parents=True, exist_ok=True)

        profile_path = docs_path / pathlib.Path(filename)
        if isinstance(model_class, dict):
            schema = model_class
        else:
            schema = model_class.model_json_schema()
        with pathlib.Path(profile_path).open("w") as f:
            json.dump(schema, f, indent=2)
        logger.info("%s file on directory '%s' is updated.", filename, docs_path)
        schema_file_path = schema_path / pathlib.Path(filename)
        with pathlib.Path(schema_file_path).open("w") as f:
            json.dump(schema, f, indent=2)
        logger.info("%s file on directory '%s' is updated.", filename, schema_path)


if __name__ == "__main__":
    set_basic_logging_config()
    update_schema_files()
