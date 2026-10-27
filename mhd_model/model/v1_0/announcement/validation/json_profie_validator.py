import pathlib
from typing import Any

import orjson
from cachetools import TTLCache, cached
from jsonprofile.profile.base import ValidationRuntimeConfiguration
from jsonprofile.validator import JsonValidator

from mhd_model.model.definitions import ANNOUNCEMENT_FILE_V1_0_DEFAULT_SCHEMA_NAME
from mhd_model.model.v1_0.announcement.profiles.base_profile import (
    BASE_ANNOUNCEMENT_FILE_PROFILE_v1_0,
)
from mhd_model.model.v1_0.announcement.profiles.legacy_profile import (
    LEGACY_ANNOUNCEMENT_FILE_PROFILE_v1_0,
)
from mhd_model.model.v1_0.announcement.profiles.ms_profile import (
    MS_ANNOUNCEMENT_FILE_PROFILE_v1_0,
)
from mhd_model.schema_utils import load_mhd_json_schema
from mhd_model.shared.mhd_cv_term_search import MhdCvTermSearch
from mhd_model.shared.model import ProfileEnabledDataset
from mhd_model.shared.ontology_lookup_cv_term_search import OntologyLookupCvTermSearch
from mhd_model.shared.validation.base import BaseAnnouncementFileValidator


@cached(cache=TTLCache(maxsize=10, ttl=3600 * 24))
def new_announcement_validator(
    profile_uri: str,
    ontology_lookup_file_path: None | str = None,
) -> JsonValidator:

    _, json_schema = load_mhd_json_schema(
        uri=ANNOUNCEMENT_FILE_V1_0_DEFAULT_SCHEMA_NAME
    )

    _, base_profile = load_mhd_json_schema(uri=BASE_ANNOUNCEMENT_FILE_PROFILE_v1_0.id)

    _, legacy_profile = load_mhd_json_schema(
        uri=LEGACY_ANNOUNCEMENT_FILE_PROFILE_v1_0.id
    )
    _, ms_profile = load_mhd_json_schema(uri=MS_ANNOUNCEMENT_FILE_PROFILE_v1_0.id)
    profiles = {
        BASE_ANNOUNCEMENT_FILE_PROFILE_v1_0.id: base_profile,
        LEGACY_ANNOUNCEMENT_FILE_PROFILE_v1_0.id: legacy_profile,
        MS_ANNOUNCEMENT_FILE_PROFILE_v1_0.id: ms_profile,
    }
    active_profile = profiles.get(profile_uri)
    if ontology_lookup_file_path:
        mhd_cv_term_search = OntologyLookupCvTermSearch(
            db_path=ontology_lookup_file_path
        )
    else:
        mhd_cv_term_search = MhdCvTermSearch()
    validator = JsonValidator(
        json_schema=json_schema,
        profile=active_profile,
        referenced_profiles={
            BASE_ANNOUNCEMENT_FILE_PROFILE_v1_0.id: base_profile,
            LEGACY_ANNOUNCEMENT_FILE_PROFILE_v1_0.id: legacy_profile,
            MS_ANNOUNCEMENT_FILE_PROFILE_v1_0.id: ms_profile,
        },
        default_cv_term_search=mhd_cv_term_search,
    )
    return validator


class MhdAnnouncementFileJsonProfileValidator_v1_0(BaseAnnouncementFileValidator):
    def validate(
        self,
        announcement_file_json: dict[str, Any],
        ontology_lookup_file_path: None | str = None,
    ) -> list[str]:
        profile: ProfileEnabledDataset = ProfileEnabledDataset.model_validate(
            announcement_file_json
        )
        ontology_lookup_db_path = None
        if (
            ontology_lookup_file_path
            and pathlib.Path(ontology_lookup_file_path).exists()
        ):
            ontology_lookup_db_path = ontology_lookup_file_path
        validator = new_announcement_validator(
            profile_uri=profile.profile_uri,
            ontology_lookup_file_path=ontology_lookup_db_path,
        )
        runtime_config = ValidationRuntimeConfiguration()
        result = validator.validate_dict(
            announcement_file_json, runtime_config=runtime_config
        )
        errors = []
        for k, v in result.errors.items():
            for message in v:
                errors.append(
                    f"{k}: {message.code}, {message.enforcement_level.name}, {message.message}"
                )
        return errors

    def validate_file(
        self,
        announcement_file_path: pathlib.Path,
        ontology_lookup_file_path: None | str = None,
    ) -> list[str]:
        dict_object = orjson.loads(announcement_file_path.read_bytes())
        return self.validate(
            announcement_file_json=dict_object,
            ontology_lookup_file_path=ontology_lookup_file_path,
        )
