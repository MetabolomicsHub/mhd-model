import logging

from jsonprofile.profile.base import (
    BaseCvTerm,
)
from jsonprofile.profile.constraints import constraints
from jsonprofile.profile.model import (
    FieldRequirement,
    FieldRequirementGroup,
    JsonProfile,
    JsonProfileConfiguration,
)

from mhd_model.model.definitions import (
    ANNOUNCEMENT_FILE_V1_0_BASE_PROFILE_NAME,
    ANNOUNCEMENT_FILE_V1_0_LEGACY_PROFILE_NAME,
)
from mhd_model.model.v1_0.announcement.profiles.base_profile import MHD_CV_TERM_MAPPING

logger = logging.getLogger(__name__)


LEGACY_ANNOUNCEMENT_FILE_PROFILE_v1_0 = JsonProfile(
    id=ANNOUNCEMENT_FILE_V1_0_LEGACY_PROFILE_NAME,
    extends=ANNOUNCEMENT_FILE_V1_0_BASE_PROFILE_NAME,
    version="v1.0",
    name="MetabolomicsHub Announcement File v1.0 Legacy Profile",
    description="MetabolomicsHub Announcement File v1.0 Legacy Profile",
    configuration=JsonProfileConfiguration(cv_term_field_mapping=MHD_CV_TERM_MAPPING),
    requirements={
        "$": FieldRequirementGroup(
            requirements=[
                FieldRequirement(
                    code="legacy-required-0001",
                    required_properties=[
                        "id",
                        "$schema",
                        "profile_uri",
                        "type",
                        "uri",
                        "mhd_metadata_file_url",
                        "cv_definitions",
                        "repository_name",
                        "repository_short_name",
                        "repository_identifier",
                        "license",
                        "url_list",
                        "name",
                        "description",
                        "submission_date",
                        "public_release_date",
                        "submitters",
                        "repository_metadata_file_list",
                    ],
                    recommended_properties=[
                        "principal_investigators",
                        "characteristic_values",
                        "protocols",
                        "submitter_keywords",
                        "raw_data_file_list",
                        "result_file_list",
                        "reported_molecular_entities",
                    ],
                ),
            ]
        ),
        "$.url_list": FieldRequirement(
            code="legacy-url-list-0001",
            value_constraint=constraints.CollectionConstraint(min_occurs=1),
        ),
        "$.repository_name": FieldRequirement(
            code="legacy-repository_name-0001",
            value_constraint=constraints.StringConstraint(minimum=1),
        ),
        "$.repository_short_name": FieldRequirement(
            code="legacy-repository_short_name-0001",
            value_constraint=constraints.StringConstraint(minimum=1),
        ),
        "$.repository_identifier": FieldRequirement(
            code="legacy-repository_identifier-0001",
            value_constraint=constraints.StringConstraint(minimum=1),
        ),
        "$.license_name": FieldRequirement(
            code="legacy-license-name-0001",
            value_constraint=constraints.StringConstraint(minimum=1),
        ),
        "$.name": FieldRequirement(
            code="legacy-name-0001",
            value_constraint=constraints.StringConstraint(minimum=0),
        ),
        "$.description": FieldRequirement(
            code="legacy-description-0001",
            value_constraint=constraints.StringConstraint(),
        ),
        "$.submitters": FieldRequirement(
            code="legacy-submitters-0001",
            value_constraint=constraints.CollectionConstraint(min_occurs=1),
        ),
        "$.submitters[*].email_list": FieldRequirement(
            code="legacy-submitters_emails-0001",
            value_constraint=constraints.CollectionConstraint(min_occurs=1),
        ),
        "$.principal_investigators": FieldRequirement(
            code="legacy-principal_investigators-0001",
            value_constraint=constraints.CollectionConstraint(min_occurs=1),
        ),
        "$.principal_investigators[*].email_list": FieldRequirement(
            code="legacy-principal_investigators-email_list_0001",
            value_constraint=constraints.CollectionConstraint(min_occurs=1),
        ),
        "$.characteristic_values": FieldRequirementGroup(
            requirements=[
                FieldRequirement(
                    code="legacy-characteristic_values-0001",
                    value_constraint=constraints.CollectionConstraint(
                        description="There must be a characteristic named 'Organism' in characteristic_values",
                        item_value_jsonpath_list=[".[*].key"],
                        item_value_match_constraint=constraints.CVTermEnumConstraint(
                            allowed_cv_terms=[
                                BaseCvTerm(
                                    cv_label="NCIT",
                                    cv_accession="NCIT:C14250",
                                    name="Organism",
                                )
                            ]
                        ),
                        min_referenced_value_match=1,
                        max_referenced_value_match=1,
                    ),
                ),
            ]
        ),
    },
)
