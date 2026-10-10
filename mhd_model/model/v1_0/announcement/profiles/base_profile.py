import logging

from jsonprofile.profile.base import (
    BaseCvTerm,
    CvTermFieldMapping,
)
from jsonprofile.profile.constraints import (
    CVTermConstraint,
    Evaluation,
    Precondition,
    constraints,
)
from jsonprofile.profile.model import (
    FieldRequirement,
    FieldRequirementGroup,
    JsonProfile,
    JsonProfileConfiguration,
)

from mhd_model.model.definitions import (
    ANNOUNCEMENT_FILE_V1_0_BASE_PROFILE_NAME,
)
from mhd_model.model.v1_0.rules.managed_cv_terms import MISSING_PUBLICATION_REASON
from mhd_model.shared.base import CvTerm

logger = logging.getLogger(__name__)

MHD_CV_TERM_MAPPING = CvTermFieldMapping(
    label_field="source",
    accession_field="accession",
    name_field="name",
    value_field="value",
)


def get_list_from_common_terms(
    terms: list[CvTerm] | dict[str, CvTerm],
) -> list[BaseCvTerm]:
    if isinstance(terms, dict):
        terms = list(terms.values())
    return [
        BaseCvTerm(cv_label=x.source, cv_accession=x.accession, name=x.name)
        for x in terms
    ]


missing_publication_reasons = get_list_from_common_terms(MISSING_PUBLICATION_REASON)


BASE_ANNOUNCEMENT_FILE_PROFILE_v1_0 = JsonProfile(
    id=ANNOUNCEMENT_FILE_V1_0_BASE_PROFILE_NAME,
    version="v1.0",
    name="MetabolomicsHub Announcement File v1.0 Base Profile",
    description="MetabolomicsHub Announcement File v1.0 Base Profile",
    configuration=JsonProfileConfiguration(cv_term_field_mapping=MHD_CV_TERM_MAPPING),
    requirements={
        "$": FieldRequirementGroup(
            requirements=[
                FieldRequirement(
                    code="base-required-0001",
                    enforcement_level="required",
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
                    ],
                    recommended_properties=[
                        "license",
                        "license_name",
                        "mhd_metadata_file_hashes",
                        "submitter_keywords",
                        "reported_molecular_entities",
                        "repository_metadata_file_list",
                        "raw_data_file_list",
                        "result_file_list",
                    ],
                ),
            ]
        ),
        "$.tag_list[*]": FieldRequirement(
            code="base-tag_list-0001", recommended_properties=["key", "value"]
        ),
        "$.tag_list[*].key": FieldRequirementGroup(
            requirements=[
                FieldRequirement(
                    code="base-tag_list-key-0001",
                    value_constraint=constraints.NotNullConstraint(
                        precondition=Precondition(
                            evaluations=[
                                Evaluation(
                                    constraint=constraints.StringConstraint(
                                        exceptional_values=[None]
                                    )
                                )
                            ],
                        ),
                        null_values=[None, ""],
                    ),
                ),
                FieldRequirement(
                    code="base-tag_list-key-0002",
                    value_constraint=constraints.NotNullConstraint(
                        precondition=Precondition(
                            evaluations=[
                                Evaluation(
                                    constraint=CVTermConstraint(
                                        allow_user_defined_terms=True,
                                        allow_synonym=True,
                                    )
                                )
                            ],
                        ),
                    ),
                ),
            ]
        ),
        "$.tag_list[*].value": FieldRequirement(
            code="base-tag_list-0004",
            value_constraint=constraints.NotNullConstraint(null_values=[None, ""]),
        ),
        "$.repository_revision": FieldRequirement(
            code="base-repository_revision-0001",
            value_constraint=constraints.IntegerConstraint(minimum=0),
        ),
        "$.repository_revision_comment": FieldRequirement(
            code="base-repository_revision_comment-0001",
            value_constraint=constraints.StringConstraint(minimum=0),
        ),
        "$.repository_revision_datetime": FieldRequirement(
            code="base-repository_revision_datetime-0001",
            value_constraint=constraints.DateTimeConstraint(),
        ),
        "$.change_log": FieldRequirement(
            code="base-change_log-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.change_log[*]": FieldRequirement(
            code="base-change_log-revision-0001",
            required_properties=["revision", "revision_datetime"],
        ),
        "$.change_log[*].revision": FieldRequirement(
            code="base-change_log-revision-0002",
            match_is_required=True,
            value_constraint=constraints.IntegerConstraint(minimum=0),
        ),
        "$.change_log[*].revision_datetime": FieldRequirement(
            code="base-change_log-revision-0003",
            value_constraint=constraints.DateTimeConstraint(),
        ),
        "$.change_log[*].comment": FieldRequirement(
            code="base-change_log-revision-0004",
            value_constraint=constraints.StringConstraint(minimum=0),
        ),
        "$['$schema']": FieldRequirement(
            code="base-schema-0001",
            value_constraint=constraints.StringConstraint(minimum=10),
        ),
        "$.profile_uri": FieldRequirement(
            code="base-profile_uri-0001",
            value_constraint=constraints.StringConstraint(minimum=10),
        ),
        "$.created_at": FieldRequirement(
            code="base-created_at-0001",
            value_constraint=constraints.DateTimeConstraint(),
        ),
        "$.id": FieldRequirement(
            code="base-id-0001",
            value_constraint=constraints.StringConstraint(minimum=10),
        ),
        "$.type": FieldRequirement(
            code="base-type-0001",
            value_constraint=constraints.StringConstraint(minimum=1),
        ),
        "$.url_list": FieldRequirement(
            code="base-url-list-0001",
            value_constraint=constraints.CollectionConstraint(min_occurs=0),
        ),
        "$.url_list[*]": FieldRequirement(
            code="base-url-list-0002",
            value_constraint=constraints.UriConstraint(
                allowed_schemes=["http", "https", "ftp"]
            ),
        ),
        "$.uri": FieldRequirement(
            code="base-uri-0001",
            value_constraint=constraints.UriConstraint(),
        ),
        "$.repository_identifier": FieldRequirement(
            code="base-repository_identifier-0001",
            value_constraint=constraints.StringConstraint(),
        ),
        "$.alternative_id_list": FieldRequirement(
            code="base-alternative_id_list-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.alternative_id_list[*]": FieldRequirement(
            code="base-alternative_id_list-0002",
            value_constraint=constraints.StringConstraint(minimum=10),
        ),
        "$.repository_name": FieldRequirement(
            code="base-repository_name-0001",
            value_constraint=constraints.StringConstraint(),
        ),
        "$.repository_short_name": FieldRequirement(
            code="base-repository_short_name-0001",
            value_constraint=constraints.StringConstraint(),
        ),
        "$.license": FieldRequirement(
            code="base-license-0001",
            value_constraint=constraints.UriConstraint(
                allowed_schemes=["http", "https"]
            ),
        ),
        "$.license_name": FieldRequirement(
            code="base-license-name-0001",
            value_constraint=constraints.StringConstraint(minimum=0),
        ),
        "$.name": FieldRequirement(
            code="base-name-0001",
            value_constraint=constraints.StringConstraint(minimum=0),
        ),
        "$.description": FieldRequirement(
            code="base-description-0001",
            value_constraint=constraints.StringConstraint(),
        ),
        "$.cv_definitions": FieldRequirement(
            code="base-cv_definitions-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.cv_definitions[*]": FieldRequirement(
            code="base-cv_definitions-definition-0001",
            required_properties=["label", "name", "uri"],
        ),
        "$.cv_definitions[*].label": FieldRequirement(
            code="base-cv_definitions-definition-0002",
            value_constraint=constraints.StringConstraint(minimum=1),
        ),
        "$.cv_definitions[*].name": FieldRequirement(
            code="base-cv_definitions-definition-0003",
            value_constraint=constraints.StringConstraint(),
        ),
        "$.cv_definitions[*].uri": FieldRequirement(
            code="base-cv_definitions-definition-0004",
            value_constraint=constraints.UriConstraint(exceptional_values=[""]),
        ),
        "$.cv_definitions[*].prefix": FieldRequirement(
            code="base-cv_definitions-prefix-0005",
            value_constraint=constraints.StringConstraint(),
        ),
        "$.cv_definitions[*].version": FieldRequirement(
            code="base-cv_definitions-version-0006",
            value_constraint=constraints.StringConstraint(),
        ),
        "$.mhd_identifier": FieldRequirement(
            code="base-mhd_identifier-0001",
            value_constraint=constraints.StringConstraint(minimum=9, maximum=12),
        ),
        "$.mhd_metadata_file_url": FieldRequirement(
            code="base-mhd_metadata_file_url-0001",
            value_constraint=constraints.UriConstraint(
                allowed_schemes=["http", "https"]
            ),
        ),
        "$.mhd_metadata_file_hashes": FieldRequirement(
            code="base-mhd_metadata_file_hashes-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.mhd_metadata_file_hashes[*]": FieldRequirement(
            code="base-mhd_metadata_file_hashes_hash-0001",
            required_properties=["name", "value"],
            value_constraint=constraints.CVTermConstraint(
                is_cv_term_value_required=True,
                allow_user_defined_terms=True,
                allow_synonym=True,
            ),
        ),
        "$.mhd_metadata_file_hashes[*].value": FieldRequirement(
            code="base-mhd_metadata_file_hashes_hash-0002",
            value_constraint=constraints.StringConstraint(minimum=32),
        ),
        "$.mhd_metadata_file_hashes[*].name": FieldRequirement(
            code="base-mhd_metadata_file_hashes_hash-0003",
            value_constraint=constraints.StringConstraint(minimum=2),
        ),
        "$.submission_date": FieldRequirement(
            code="base-submission_date-0001",
            value_constraint=constraints.DateTimeConstraint(),
        ),
        "$.public_release_date": FieldRequirement(
            code="base-public_release_date-0001",
            value_constraint=constraints.DateTimeConstraint(),
        ),
        "$.submitters": FieldRequirement(
            code="base-submitters-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.submitters[*]": FieldRequirement(
            code="base-submitters-0002", required_properties=["full_name", "email_list"]
        ),
        "$.submitters[*].full_name": FieldRequirement(
            code="base-submitters-full_name-0001",
            value_constraint=constraints.StringConstraint(minimum=5),
        ),
        "$.submitters[*].email_list": FieldRequirement(
            code="base-submitters_email_list-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.submitters[*].email_list[*]": FieldRequirement(
            code="base-submitters-email_list-0002",
            value_constraint=constraints.EmailConstraint(),
        ),
        "$.submitters[*].orcid": FieldRequirement(
            code="base-submitters-orcid-0002",
            value_constraint=constraints.RegexConstraint(
                pattern=r"^[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[X0-9]$",
            ),
        ),
        "$.submitters[*].affiliation_list": FieldRequirement(
            code="base-submitters-affiliation_list-0001",
            value_constraint=constraints.CollectionConstraint(min_match=1),
        ),
        "$.principal_investigators": FieldRequirement(
            code="base-principal_investigators-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.principal_investigators[*]": FieldRequirement(
            code="base-principal_investigators-0002",
            required_properties=["full_name", "email_list"],
        ),
        "$.principal_investigators[*].full_name": FieldRequirement(
            code="base-principal_investigators_full_name-0001",
            value_constraint=constraints.StringConstraint(minimum=5),
        ),
        "$.principal_investigators[*].email_list": FieldRequirement(
            code="base-principal_investigators-email_list_0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.principal_investigators[*].email_list[*]": FieldRequirement(
            code="base-principal_investigators-email_list_0002",
            value_constraint=constraints.EmailConstraint(),
        ),
        "$.omics_type": FieldRequirement(
            code="base-omics_type-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.omics_type[*]": FieldRequirement(
            code="base-omics_type-0002",
            value_constraint=constraints.CVTermConstraint(
                allow_user_defined_terms=True,
                allow_synonym=True,
            ),
        ),
        "$.technology_type": FieldRequirement(
            code="base-technology_type-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.technology_type[*]": FieldRequirement(
            code="base-technology_type-0002",
            value_constraint=constraints.CVTermConstraint(
                allow_user_defined_terms=True,
                allow_synonym=True,
            ),
        ),
        "$.measurement_type": FieldRequirement(
            code="base-measurement_type-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.measurement_type[*]": FieldRequirement(
            code="base-measurement_type-0002",
            value_constraint=constraints.CVTermConstraint(
                allow_user_defined_terms=True,
                allow_synonym=True,
            ),
        ),
        "$.assay_type": FieldRequirement(
            code="base-assay_type-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.assay_type[*]": FieldRequirement(
            code="base-assay_type-0002",
            value_constraint=constraints.CVTermConstraint(
                allow_user_defined_terms=True,
                allow_synonym=True,
            ),
        ),
        "$.submitter_keywords": FieldRequirement(
            code="base-submitter_keywords-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.submitter_keywords[*]": FieldRequirement(
            code="base-submitter_keywords-0002",
            value_constraint=constraints.CVTermConstraint(
                allow_user_defined_terms=True,
                allow_synonym=True,
            ),
        ),
        "$.descriptors": FieldRequirement(
            code="base-descriptors-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.descriptors[*]": FieldRequirement(
            code="base-descriptors-0002",
            value_constraint=constraints.CVTermConstraint(
                allow_user_defined_terms=True,
                allow_synonym=True,
            ),
        ),
        "$.publications": FieldRequirement(
            code="base-publications-0001",
            description="Publication must be defined or annotated with a missing cv term",
            value_constraint=constraints.ConstraintGroup(
                join_operator="or",
                min_valid=1,
                constraints=[
                    constraints.CollectionConstraint(min_occurs=1),
                    constraints.CVTermEnumConstraint(
                        allowed_cv_terms=missing_publication_reasons,
                    ),
                ],
            ),
        ),
        "$.publications[*].doi": FieldRequirement(
            code="base-publications-0010",
            description="Publication DOI must be valid",
            value_constraint=constraints.RegexConstraint(
                pattern=r"^10[.].+/.+$",
            ),
        ),
        "$.publications[*].pubmed_id": FieldRequirement(
            code="base-publications-0011",
            description="Publication PubMed Id must be valid",
            value_constraint=constraints.RegexConstraint(
                pattern=r"^[0-9]{1,20}$",
            ),
        ),
        "$.publications[*].title": FieldRequirement(
            code="base-publications-0012",
            description="Publication title must be valid",
            value_constraint=constraints.StringConstraint(minimum=5),
        ),
        "$.publications[*].author_list[*]": FieldRequirement(
            code="base-publications-0013",
            description="Publication author must be valid",
            value_constraint=constraints.StringConstraint(minimum=2),
        ),
        "$.study_factors": FieldRequirement(
            code="base-study_factors-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.study_factors[*]": FieldRequirement(
            code="base-study_factors-factor-0001", required_properties=["key"]
        ),
        "$.study_factors[*].key": FieldRequirement(
            code="base-study_factors-factor-0002",
            value_constraint=constraints.CVTermConstraint(
                allow_user_defined_terms=True,
                allow_synonym=True,
            ),
        ),
        "$.study_factors[*].values": FieldRequirement(
            code="base-study_factors-factor-0003",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.study_factors[*].values[*]": FieldRequirement(
            code="base-study_factors-factor-0004-01",
            value_constraint=constraints.ConstraintGroup(
                join_operator="or",
                min_valid=1,
                constraints=[
                    constraints.CVTermConstraint(
                        allow_user_defined_terms=True,
                        allow_synonym=True,
                    ),
                    constraints.StringConstraint(json_path=".value", minimum=1),
                ],
            ),
        ),
        "$.study_factors[*].values[*].unit": FieldRequirement(
            code="base-study_factors-factor-unit-0001",
            value_constraint=constraints.CVTermConstraint(
                allow_user_defined_terms=True,
                allow_synonym=True,
            ),
        ),
        "$.characteristic_values": FieldRequirement(
            code="base-characteristic_values-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.characteristic_values[*]": FieldRequirement(
            code="base-characteristic_values-characteristic-0001",
            required_properties=["key"],
        ),
        "$.characteristic_values[*].key": FieldRequirement(
            code="base-characteristic_values-characteristic-0002",
            value_constraint=constraints.CVTermConstraint(
                allow_user_defined_terms=True,
                allow_synonym=True,
            ),
        ),
        "$.characteristic_values[*].values": FieldRequirement(
            code="base-characteristic_values-characteristic-0003",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.characteristic_values[*].values[*]": FieldRequirement(
            code="base-characteristic_values-characteristic-0004-01",
            value_constraint=constraints.ConstraintGroup(
                join_operator="or",
                min_valid=1,
                constraints=[
                    constraints.CVTermConstraint(
                        allow_user_defined_terms=True,
                        allow_synonym=True,
                        exceptional_cv_list=["ILX", "wikidata"],
                    ),
                    constraints.StringConstraint(json_path=".value", minimum=1),
                ],
            ),
        ),
        "$.characteristic_values[*].values[*].unit": FieldRequirement(
            code="base-characteristic_values-characteristic-unit-0001",
            value_constraint=constraints.CVTermConstraint(
                allow_user_defined_terms=True,
                allow_synonym=True,
            ),
        ),
        "$.protocols": FieldRequirement(
            code="base-protocols-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.protocols[*]": FieldRequirement(
            code="base-protocols-protocol-0001", required_properties=["name"]
        ),
        "$.protocols[*].protocol_type": FieldRequirement(
            code="base-protocols-protocol_type-0001",
            value_constraint=constraints.CVTermConstraint(
                allow_user_defined_terms=True,
                allow_synonym=True,
            ),
        ),
        "$.protocols[*].description": FieldRequirement(
            code="base-protocols-description-0001",
            value_constraint=constraints.StringConstraint(),
        ),
        "$.protocols[*].protocol_parameters": FieldRequirement(
            code="base-protocols-protocol_parameters-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.protocols[*].protocol_parameters[*]": FieldRequirement(
            code="base-protocols-protocol_parameters-0002", required_properties=["key"]
        ),
        "$.protocols[*].protocol_parameters[*].key": FieldRequirement(
            code="base-protocols-protocol_parameters-0003",
            value_constraint=constraints.CVTermConstraint(
                allow_user_defined_terms=True,
                allow_synonym=True,
            ),
        ),
        "$.protocols[*].protocol_parameters[*].values": FieldRequirement(
            code="base-protocols-protocol_parameters-0004",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.protocols[*].protocol_parameters[*].values[*]": FieldRequirement(
            code="base-characteristic_values-characteristic-0004-01",
            value_constraint=constraints.ConstraintGroup(
                join_operator="or",
                min_valid=1,
                constraints=[
                    constraints.CVTermConstraint(
                        allow_user_defined_terms=True,
                        allow_synonym=True,
                        exceptional_cv_list=["ILX", "wikidata"],
                    ),
                    constraints.StringConstraint(json_path=".value", minimum=1),
                ],
            ),
        ),
        "$.protocols[*].protocol_parameters[*].values[*].unit": FieldRequirement(
            code="base-characteristic_values-characteristic-unit-0001",
            value_constraint=constraints.CVTermConstraint(
                allow_user_defined_terms=True,
                allow_synonym=True,
                exceptional_cv_list=["ILX", "wikidata"],
            ),
        ),
        "$.reported_molecular_entities": FieldRequirement(
            code="base-reported_molecular_entities-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.reported_molecular_entities[*]": FieldRequirement(
            code="base-reported_molecular_entities-0002",
            required_properties=["name"],
        ),
        "$.reported_molecular_entities[*].name": FieldRequirement(
            code="base-reported_molecular_entities-name-0001",
            value_constraint=constraints.StringConstraint(),
        ),
        "$.reported_molecular_entities[*].database_identifiers": FieldRequirement(
            code="base-reported_molecular_entities-database_identifiers-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.reported_molecular_entities[*].database_identifiers[*]": FieldRequirement(
            code="base-reported_molecular_entities-database_identifiers-0002",
            value_constraint=constraints.CVTermConstraint(
                allow_user_defined_terms=True,
                allow_synonym=True,
            ),
        ),
        "$.repository_metadata_file_list": FieldRequirement(
            code="base-repository_metadata_file_list-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.repository_metadata_file_list[*]": FieldRequirement(
            code="base-repository_metadata_file_list-0002",
            required_properties=["name", "url_list"],
        ),
        "$.repository_metadata_file_list[*].url_list[*]": FieldRequirement(
            code="base-repository_metadata_file_list-url_list-0001",
            value_constraint=constraints.UriConstraint(
                allowed_schemes=["http", "https", "ftp"]
            ),
        ),
        "$.repository_metadata_file_list[*].name": FieldRequirement(
            code="base-repository_metadata_file_list-name-0001",
            value_constraint=constraints.StringConstraint(),
        ),
        "$.repository_metadata_file_list[*].format": FieldRequirement(
            code="base-repository_metadata_file_list-format-0002",
            value_constraint=constraints.CVTermConstraint(allow_synonym=True),
        ),
        "$.repository_metadata_file_list[*].compression_formats[*]": FieldRequirement(
            code="base-repository_metadata_file_list-compression_formats-0002",
            value_constraint=constraints.CVTermConstraint(allow_synonym=True),
        ),
        "$.repository_metadata_file_list[*].extension": FieldRequirement(
            code="base-repository_metadata_file_list-extension-0001",
            value_constraint=constraints.StringConstraint(),
        ),
        "$.raw_data_file_list": FieldRequirement(
            code="base-raw_data_file_list-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.raw_data_file_list[*]": FieldRequirement(
            code="base-raw_data_file_list-0002",
            required_properties=["name", "url_list"],
        ),
        "$.raw_data_file_list[*].url_list[*]": FieldRequirement(
            code="base-raw_data_file_list-url_list-0001",
            value_constraint=constraints.UriConstraint(
                allowed_schemes=["http", "https", "ftp"]
            ),
        ),
        "$.raw_data_file_list[*].name": FieldRequirement(
            code="base-raw_data_file_list-name-0001",
            value_constraint=constraints.StringConstraint(),
        ),
        "$.raw_data_file_list[*].format": FieldRequirement(
            code="base-raw_data_file_list-format-0002",
            value_constraint=constraints.CVTermConstraint(allow_synonym=True),
        ),
        "$.raw_data_file_list[*].compression_formats[*]": FieldRequirement(
            code="base-raw_data_file_list-compression_formats-0002",
            value_constraint=constraints.CVTermConstraint(allow_synonym=True),
        ),
        "$.raw_data_file_list[*].extension": FieldRequirement(
            code="base-raw_data_file_list-extension-0001",
            value_constraint=constraints.StringConstraint(),
        ),
        "$.result_file_list": FieldRequirement(
            code="base-result_file_list-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.result_file_list[*]": FieldRequirement(
            code="base-result_file_list-0002",
            required_properties=["name", "url_list"],
        ),
        "$.result_file_list[*].url_list[*]": FieldRequirement(
            code="base-result_file_list-url_list-0001",
            value_constraint=constraints.UriConstraint(
                allowed_schemes=["http", "https", "ftp"]
            ),
        ),
        "$.result_file_list[*].name": FieldRequirement(
            code="base-result_file_list-name-0001",
            value_constraint=constraints.StringConstraint(),
        ),
        "$.result_file_list[*].format": FieldRequirement(
            code="base-result_file_list-format-0002",
            value_constraint=constraints.CVTermConstraint(allow_synonym=True),
        ),
        "$.result_file_list[*].compression_formats[*]": FieldRequirement(
            code="base-result_file_list-compression_formats-0002",
            value_constraint=constraints.CVTermConstraint(allow_synonym=True),
        ),
        "$.result_file_list[*].extension": FieldRequirement(
            code="base-result_file_list-extension-0001",
            value_constraint=constraints.StringConstraint(),
        ),
        "$.derived_data_file_list": FieldRequirement(
            code="base-derived_data_file_list-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.derived_data_file_list[*]": FieldRequirement(
            code="base-derived_data_file_list-0002",
            required_properties=["name", "url_list"],
        ),
        "$.derived_data_file_list[*].url_list[*]": FieldRequirement(
            code="base-derived_data_file_list-url_list-0001",
            value_constraint=constraints.UriConstraint(
                allowed_schemes=["http", "https", "ftp"]
            ),
        ),
        "$.derived_data_file_list[*].name": FieldRequirement(
            code="base-derived_data_file_list-name-0001",
            value_constraint=constraints.StringConstraint(),
        ),
        "$.derived_data_file_list[*].format": FieldRequirement(
            code="base-derived_data_file_list-format-0002",
            value_constraint=constraints.CVTermConstraint(allow_synonym=True),
        ),
        "$.derived_data_file_list[*].compression_formats[*]": FieldRequirement(
            code="base-derived_data_file_list-compression_formats-0002",
            value_constraint=constraints.CVTermConstraint(allow_synonym=True),
        ),
        "$.derived_data_file_list[*].extension": FieldRequirement(
            code="base-derived_data_file_list-extension-0001",
            value_constraint=constraints.StringConstraint(),
        ),
        "$.supplementary_file_list": FieldRequirement(
            code="base-supplementary_file_list-0001",
            value_constraint=constraints.CollectionConstraint(),
        ),
        "$.supplementary_file_list[*]": FieldRequirement(
            code="base-supplementary_file_list-0002",
            required_properties=["name", "url_list"],
        ),
        "$.supplementary_file_list[*].url_list[*]": FieldRequirement(
            code="base-supplementary_file_list-url_list-0001",
            value_constraint=constraints.UriConstraint(
                allowed_schemes=["http", "https", "ftp"]
            ),
        ),
        "$.supplementary_file_list[*].name": FieldRequirement(
            code="base-supplementary_file_list-name-0001",
            value_constraint=constraints.StringConstraint(),
        ),
        "$.supplementary_file_list[*].format": FieldRequirement(
            code="base-supplementary_file_list-format-0002",
            value_constraint=constraints.CVTermConstraint(allow_synonym=True),
        ),
        "$.supplementary_file_list[*].compression_formats[*]": FieldRequirement(
            code="base-supplementary_file_list-compression_formats-0002",
            value_constraint=constraints.CVTermConstraint(allow_synonym=True),
        ),
        "$.supplementary_file_list[*].extension": FieldRequirement(
            code="base-supplementary_file_list-extension-0001",
            value_constraint=constraints.StringConstraint(),
        ),
    },
)
