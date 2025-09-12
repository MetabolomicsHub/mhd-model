from typing import Annotated

from pydantic import BaseModel, Field

from mhd_model.model.v0_1.announcement.profiles.base.profile import (
    AnnouncementBaseProfile,
)
from mhd_model.model.v0_1.announcement.profiles.legacy.profile import (
    AnnouncementLegacyProfile,
)
from mhd_model.model.v0_1.announcement.profiles.ms.profile import AnnouncementMsProfile
from mhd_model.model.v0_1.dataset.profiles.base.profile import MhDatasetBaseProfile
from mhd_model.model.v0_1.dataset.profiles.legacy.profile import MhDatasetLegacyProfile
from mhd_model.model.v0_1.dataset.profiles.ms.profile import MhDatasetMsProfile

from . import v0_1


class SupportedJsonSchema(BaseModel):
    uri: str
    file_path: Annotated[str, Field(exclude=True)]
    class_type: Annotated[str, Field(exclude=True)]


class SupportedSchema(SupportedJsonSchema):
    default_profile_uri: str
    supported_profiles: dict[str, SupportedJsonSchema]


class SupportedSchemaMap(BaseModel):
    default_schema_uri: str
    schemas: dict[str, SupportedSchema]


ANNOUNCEMENT_FILE_V0_1_DEFAULT_SCHEMA_NAME = "https://metabolomicshub.github.io/mhd-model/schemas/v0_1/announcement-v0.1.schema.json"
ANNOUNCEMENT_FILE_V0_1_MS_PROFILE_NAME = "https://metabolomicshub.github.io/mhd-model/schemas/v0_1/announcement-v0.1.schema.ms-profile.json"
ANNOUNCEMENT_FILE_V0_1_LEGACY_PROFILE_NAME = "https://metabolomicshub.github.io/mhd-model/schemas/v0_1/announcement-v0.1.schema.legacy-profile.json"

MHD_MODEL_V0_1_DEFAULT_SCHEMA_NAME = "https://metabolomicshub.github.io/mhd-model/schemas/v0_1/common-data-model-v0.1.schema.json"
MHD_MODEL_V0_1_MS_PROFILE_NAME = "https://metabolomicshub.github.io/mhd-model/schemas/v0_1/common-data-model-v0.1.ms-profile.json"
MHD_MODEL_V0_1_LEGACY_PROFILE_NAME = "https://metabolomicshub.github.io/mhd-model/schemas/v0_1/common-data-model-v0.1.legacy-profile.json"

SUPPORTED_SCHEMA_MAP = SupportedSchemaMap(
    default_schema_uri=ANNOUNCEMENT_FILE_V0_1_DEFAULT_SCHEMA_NAME,
    schemas={
        ANNOUNCEMENT_FILE_V0_1_DEFAULT_SCHEMA_NAME: SupportedSchema(
            uri=ANNOUNCEMENT_FILE_V0_1_DEFAULT_SCHEMA_NAME,
            file_path="mhd_model/schemas/mhd/announcement-v0.1.schema.json",
            class_type=AnnouncementBaseProfile.__qualname__,
            default_profile_uri=ANNOUNCEMENT_FILE_V0_1_MS_PROFILE_NAME,
            supported_profiles={
                ANNOUNCEMENT_FILE_V0_1_MS_PROFILE_NAME: SupportedJsonSchema(
                    uri=ANNOUNCEMENT_FILE_V0_1_MS_PROFILE_NAME,
                    file_path="mhd_model/schemas/mhd/announcement-v0.1.schema.ms-profile.json",
                    class_type=AnnouncementMsProfile.__qualname__,
                ),
                ANNOUNCEMENT_FILE_V0_1_LEGACY_PROFILE_NAME: SupportedJsonSchema(
                    uri=ANNOUNCEMENT_FILE_V0_1_LEGACY_PROFILE_NAME,
                    file_path="mhd_model/schemas/mhd/announcement-v0.1.schema.legacy-profile.json",
                    class_type=AnnouncementLegacyProfile.__qualname__,
                ),
            },
        ),
        MHD_MODEL_V0_1_DEFAULT_SCHEMA_NAME: SupportedSchema(
            uri=MHD_MODEL_V0_1_DEFAULT_SCHEMA_NAME,
            file_path="mhd_model/schemas/mhd/common-data-model-v0.1.schema.json",
            class_type=MhDatasetBaseProfile.__qualname__,
            default_profile_uri=MHD_MODEL_V0_1_MS_PROFILE_NAME,
            supported_profiles={
                MHD_MODEL_V0_1_MS_PROFILE_NAME: SupportedJsonSchema(
                    uri=MHD_MODEL_V0_1_MS_PROFILE_NAME,
                    file_path="mhd_model/schemas/mhd/common-data-model-v0.1.ms-profile.json",
                    class_type=MhDatasetMsProfile.__qualname__,
                ),
                MHD_MODEL_V0_1_LEGACY_PROFILE_NAME: SupportedJsonSchema(
                    uri=MHD_MODEL_V0_1_LEGACY_PROFILE_NAME,
                    file_path="mhd_model/schemas/mhd/common-data-model-v0.1.legacy-profile.json",
                    class_type=MhDatasetLegacyProfile.__qualname__,
                ),
            },
        ),
    },
)

__all__ = [
    "v0_1",
    "SupportedJsonSchema",
    "SupportedSchema",
    "SupportedSchemaMap",
    "SUPPORTED_SCHEMA_MAP",
    "ANNOUNCEMENT_FILE_V0_1_DEFAULT_SCHEMA_NAME",
    "ANNOUNCEMENT_FILE_V0_1_MS_PROFILE_NAME",
    "ANNOUNCEMENT_FILE_V0_1_LEGACY_PROFILE_NAME",
    "MHD_MODEL_V0_1_DEFAULT_SCHEMA_NAME",
    "MHD_MODEL_V0_1_MS_PROFILE_NAME",
    "MHD_MODEL_V0_1_LEGACY_PROFILE_NAME",
]
