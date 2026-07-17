import json
import logging
import pathlib

from mhd_model.log_utils import set_basic_logging_config
from mhd_model.model.v0_1.announcement.profiles.base import (
    profile as v0_1_announcement_base_profile,
)
from mhd_model.model.v0_1.announcement.profiles.legacy import (
    profile as v0_1_announcement_legacy_profile,
)
from mhd_model.model.v0_1.announcement.profiles.ms import (
    profile as v0_1_announcement_ms_profile,
)
from mhd_model.model.v0_1.dataset.profiles.base import profile as v0_1_mhd_base_profile
from mhd_model.model.v0_1.dataset.profiles.legacy import (
    profile as v0_1_mhd_legacy_profile,
)
from mhd_model.model.v0_1.dataset.profiles.ms import profile as v0_1_mhd_ms_profile
from mhd_model.model.v1_0.announcement.profiles.base import (
    profile as v1_0_announcement_base_profile,
)
from mhd_model.model.v1_0.announcement.profiles.legacy import (
    profile as v1_0_announcement_legacy_profile,
)
from mhd_model.model.v1_0.announcement.profiles.ms import (
    profile as v1_0_announcement_ms_profile,
)
from mhd_model.model.v1_0.dataset.profiles.base import profile as v1_0_mhd_base_profile
from mhd_model.model.v1_0.dataset.profiles.legacy import (
    profile as v1_0_mhd_legacy_profile,
)
from mhd_model.model.v1_0.dataset.profiles.ms import profile as v1_0_mhd_ms_profile
from scripts.update_v0_1_documentation import update_v0_1_documentation
from scripts.update_v1_0_documentation import update_v1_0_documentation

logger = logging.getLogger(__name__)


def update_schema_files() -> None:
    models = [
        (
            v0_1_announcement_base_profile.AnnouncementBaseProfile,
            "v0_1",
            "announcement-v0.1.schema.json",
        ),
        (
            v0_1_announcement_legacy_profile.AnnouncementLegacyProfile,
            "v0_1",
            "announcement-v0.1.legacy-profile.json",
        ),
        (
            v0_1_announcement_ms_profile.AnnouncementMsProfile,
            "v0_1",
            "announcement-v0.1.ms-profile.json",
        ),
        (
            v0_1_mhd_base_profile.MhDatasetBaseProfile,
            "v0_1",
            "common-data-model-v0.1.schema.json",
        ),
        (
            v0_1_mhd_legacy_profile.MhDatasetLegacyProfile,
            "v0_1",
            "common-data-model-v0.1.legacy-profile.json",
        ),
        (
            v0_1_mhd_ms_profile.MhDatasetBaseProfile,
            "v0_1",
            "common-data-model-v0.1.ms-profile.json",
        ),
        (
            v1_0_announcement_base_profile.AnnouncementBaseProfile,
            "v1_0",
            "announcement-v1.0.schema.json",
        ),
        (
            v1_0_announcement_legacy_profile.AnnouncementLegacyProfile,
            "v1_0",
            "announcement-v1.0.legacy-profile.json",
        ),
        (
            v1_0_announcement_ms_profile.AnnouncementMsProfile,
            "v1_0",
            "announcement-v1.0.ms-profile.json",
        ),
        (
            v1_0_mhd_base_profile.MhDatasetBaseProfile,
            "v1_0",
            "common-data-model-v1.0.schema.json",
        ),
        (
            v1_0_mhd_legacy_profile.MhDatasetLegacyProfile,
            "v1_0",
            "common-data-model-v1.0.legacy-profile.json",
        ),
        (
            v1_0_mhd_ms_profile.MhDatasetMsProfile,
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
    update_v0_1_documentation()
    update_v1_0_documentation()
