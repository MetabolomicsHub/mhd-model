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

__version__ = "v0.1"


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


SUPPORTED_SCHEMA_MAP = SupportedSchemaMap(
    default_schema_uri="https://www.metabolomicshub.org/schemas/v0.1/announcement-v0.1.schema.json",
    schemas={
        "https://www.metabolomicshub.org/schemas/v0.1/announcement-v0.1.schema.json": SupportedSchema(
            uri="https://www.metabolomicshub.org/schemas/v0.1/announcement-v0.1.schema.json",
            file_path="mhd_model/schemas/mhd/announcement-v0.1.schema.json",
            class_type=AnnouncementBaseProfile.__qualname__,
            default_profile_uri="https://www.metabolomicshub.org/schemas/v0.1/announcement-v0.1.schema.ms-profile.json",
            supported_profiles={
                "https://www.metabolomicshub.org/schemas/v0.1/announcement-v0.1.schema.ms-profile.json": SupportedJsonSchema(
                    uri="https://www.metabolomicshub.org/schemas/v0.1/announcement-v0.1.schema.ms-profile.json",
                    file_path="mhd_model/schemas/mhd/announcement-v0.1.schema.ms-profile.json",
                    class_type=AnnouncementMsProfile.__qualname__,
                ),
                "https://www.metabolomicshub.org/schemas/v0.1/announcement-v0.1.schema.legacy-profile.json": SupportedJsonSchema(
                    uri="https://www.metabolomicshub.org/schemas/v0.1/announcement-v0.1.schema.legacy-profile.json",
                    file_path="mhd_model/schemas/mhd/announcement-v0.1.schema.legacy-profile.json",
                    class_type=AnnouncementLegacyProfile.__qualname__,
                ),
            },
        ),
        "https://www.metabolomicshub.org/schemas/v0.1/common-data-model-v0.1.schema.json": SupportedSchema(
            uri="https://www.metabolomicshub.org/schemas/v0.1/common-data-model-v0.1.schema.json",
            file_path="mhd_model/schemas/mhd/common-data-model-v0.1.schema.json",
            class_type=MhDatasetBaseProfile.__qualname__,
            default_profile_uri="https://www.metabolomicshub.org/schemas/v0.1/common-data-model-v0.1.ms-profile.json",
            supported_profiles={
                "https://www.metabolomicshub.org/schemas/v0.1/common-data-model-v0.1.ms-profile.json": SupportedJsonSchema(
                    uri="https://www.metabolomicshub.org/schemas/v0.1/common-data-model-v0.1.ms-profile.json",
                    file_path="mhd_model/schemas/mhd/common-data-model-v0.1.ms-profile.json",
                    class_type=MhDatasetMsProfile.__qualname__,
                ),
                "https://www.metabolomicshub.org/schemas/v0.1/common-data-model-v0.1.legacy-profile.json": SupportedJsonSchema(
                    uri="https://www.metabolomicshub.org/schemas/v0.1/common-data-model-v0.1.legacy-profile.json",
                    file_path="mhd_model/schemas/mhd/common-data-model-v0.1.legacy-profile.json",
                    class_type=MhDatasetLegacyProfile.__qualname__,
                ),
            },
        ),
    },
)
