from pathlib import Path
from typing import Any

import mhd_model
from mhd_model.model.definitions import (
    MHD_MODEL_ANNOUNCEMENT_FILE_PROFILE_MAP,
    SUPPORTED_SCHEMA_MAP,
    SupportedSchema,
)
from mhd_model.utils import load_json


def load_mhd_json_schema(uri: str) -> tuple[str, dict[str, Any]]:
    for schema_uri, schema in SUPPORTED_SCHEMA_MAP.schemas.items():
        if schema_uri == uri:
            file_path = mhd_model.application_root_path / Path(schema.file_path)
            return file_path.name, load_json(file_path)
        for profile_uri, profile in schema.supported_profiles.items():
            if profile_uri == uri:
                file_path = mhd_model.application_root_path / Path(profile.file_path)
                return file_path.name, load_json(file_path)
    return None, None


def load_json_profile(profile_uri: str) -> tuple[str, dict[str, Any]]:
    schema_uri, profile_uri = MHD_MODEL_ANNOUNCEMENT_FILE_PROFILE_MAP.get(profile_uri)
    info: SupportedSchema = SUPPORTED_SCHEMA_MAP.schemas.get(schema_uri)
    profile = info.supported_profiles.get(profile_uri)
    file_path = mhd_model.application_root_path / Path(profile.file_path)
    return file_path.name, load_json(file_path)
