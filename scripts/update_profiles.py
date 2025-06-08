import json
import logging
import pathlib
import sys

from mhd.model.v0_1.announcement.profiles.base.profile import (
    AnnouncementBaseProfile,
)
from mhd.model.v0_1.announcement.profiles.legacy.profile import (
    AnnouncementLegacyProfile,
)
from mhd.model.v0_1.announcement.profiles.ms.profile import (
    AnnouncementMsProfile,
)
from mhd.model.v0_1.dataset.profiles.base.profile import MhDatasetBaseProfile
from mhd.model.v0_1.dataset.profiles.legacy.profile import MhDatasetLegacyProfile
from mhd.model.v0_1.dataset.profiles.ms.profile import MhDatasetMsProfile

logger = logging.getLogger(__name__)


def update_annoucement_file_profiles():
    profile_path = "resources/mhd/announcement-v0.1.schema.json"
    with pathlib.Path(profile_path).open("w") as f:
        json.dump(AnnouncementBaseProfile.model_json_schema(), f, indent=2)
    logger.info(
        "Base announcement profile file on directory '%s' is updated.",
        profile_path,
    )

    profile_path = "resources/mhd/announcement-v0.1.schema.ms-profile.json"
    with pathlib.Path(profile_path).open("w") as f:
        json.dump(AnnouncementMsProfile.model_json_schema(), f, indent=2)
    logger.info(
        "MS announcement profile file on directory '%s' is updated.",
        profile_path,
    )

    profile_path = "resources/mhd/announcement-v0.1.schema.legacy-profile.json"
    with pathlib.Path(profile_path).open("w") as f:
        json.dump(AnnouncementLegacyProfile.model_json_schema(), f, indent=2)
    logger.info(
        "Legacy announcement profile file on directory '%s' is updated.",
        profile_path,
    )


def update_mhd_file_profiles():
    profile_path = "resources/mhd/common-data-model-v0.1.schema.json"
    with pathlib.Path(profile_path).open("w") as f:
        json.dump(MhDatasetBaseProfile.model_json_schema(), f, indent=2)
    logger.info(
        "MHD common data model schema file on directory '%s' is updated.",
        profile_path,
    )

    profile_path = "resources/mhd/common-data-model-v0.1.ms-profile.json"
    with pathlib.Path(profile_path).open("w") as f:
        json.dump(MhDatasetMsProfile.model_json_schema(), f, indent=2)
    logger.info(
        "MHD MS common data model profile file on directory '%s' is updated.",
        profile_path,
    )

    profile_path = "resources/mhd/common-data-model-v0.1.legacy-profile.json"
    with pathlib.Path(profile_path).open("w") as f:
        json.dump(MhDatasetLegacyProfile.model_json_schema(), f, indent=2)
    logger.info(
        "MHD legacy common data model profile file on directory '%s' is updated.",
        profile_path,
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%d/%b/%Y %H:%M:%S",
        stream=sys.stdout,
    )
    update_annoucement_file_profiles()
    update_mhd_file_profiles()
