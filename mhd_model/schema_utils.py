from pathlib import Path
from typing import Any

import mhd_model
from mhd_model.model.definitions import SUPPORTED_SCHEMA_MAP
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
