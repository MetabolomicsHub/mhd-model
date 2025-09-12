from typing import Annotated

from pydantic import BaseModel, Field


class SupportedJsonSchema(BaseModel):
    uri: str
    file_path: Annotated[str, Field(exclude=True)]


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
            default_profile_uri=ANNOUNCEMENT_FILE_V0_1_MS_PROFILE_NAME,
            supported_profiles={
                ANNOUNCEMENT_FILE_V0_1_MS_PROFILE_NAME: SupportedJsonSchema(
                    uri=ANNOUNCEMENT_FILE_V0_1_MS_PROFILE_NAME,
                    file_path="mhd_model/schemas/mhd/announcement-v0.1.schema.ms-profile.json",
                ),
                ANNOUNCEMENT_FILE_V0_1_LEGACY_PROFILE_NAME: SupportedJsonSchema(
                    uri=ANNOUNCEMENT_FILE_V0_1_LEGACY_PROFILE_NAME,
                    file_path="mhd_model/schemas/mhd/announcement-v0.1.schema.legacy-profile.json",
                ),
            },
        ),
        MHD_MODEL_V0_1_DEFAULT_SCHEMA_NAME: SupportedSchema(
            uri=MHD_MODEL_V0_1_DEFAULT_SCHEMA_NAME,
            file_path="mhd_model/schemas/mhd/common-data-model-v0.1.schema.json",
            default_profile_uri=MHD_MODEL_V0_1_MS_PROFILE_NAME,
            supported_profiles={
                MHD_MODEL_V0_1_MS_PROFILE_NAME: SupportedJsonSchema(
                    uri=MHD_MODEL_V0_1_MS_PROFILE_NAME,
                    file_path="mhd_model/schemas/mhd/common-data-model-v0.1.ms-profile.json",
                ),
                MHD_MODEL_V0_1_LEGACY_PROFILE_NAME: SupportedJsonSchema(
                    uri=MHD_MODEL_V0_1_LEGACY_PROFILE_NAME,
                    file_path="mhd_model/schemas/mhd/common-data-model-v0.1.legacy-profile.json",
                ),
            },
        ),
    },
)
