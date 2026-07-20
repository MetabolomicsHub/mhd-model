from typing import Annotated

from pydantic import Field

from mhd_model.model.v1_0.announcement.profiles.base.profile import AnnouncementProtocol
from mhd_model.model.v1_0.announcement.validation.definitions import (
    CheckChildCvTermKeyValues,
    CheckCvTermKeyValue,
    CheckCvTermKeyValues,
)
from mhd_model.model.v1_0.rules.managed_cv_term_rules import (
    MANAGED_CHARACTERISTIC_VALUE_RULES,
    MANAGED_CHEMICAL_DATABASE_IDENTIFIER_RULE,
    MANAGED_FACTOR_VALUE_RULES,
    MANAGED_FILE_FORMAT_RULES,
    MANAGED_PARAMETER_VALUE_RULES,
)
from mhd_model.model.v1_0.rules.managed_cv_terms import (
    COMMON_ASSAY_TYPES,
    COMMON_CHARACTERISTIC_DEFINITIONS,
    COMMON_MEASUREMENT_TYPES,
    COMMON_OMICS_TYPES,
    COMMON_PARAMETER_DEFINITIONS,
    COMMON_PROTOCOLS,
    COMMON_TECHNOLOGY_TYPES,
    MISSING_PUBLICATION_REASON,
)
from mhd_model.shared.model import CvTerm, CvTermKeyValue, CvTermValue
from mhd_model.shared.validation.definitions import (
    AccessibleCompactURI,
    AllowAnyCvTerm,
    AllowedCvTerms,
    CvTermPlaceholder,
)

CvTermOrStr = Annotated[
    CvTerm,
    Field(
        description="Controlled Vocabulary (CV) term or plain text string keyword.",
        json_schema_extra={
            "profileValidation": AllowAnyCvTerm(
                allowed_placeholder_values=[CvTermPlaceholder()],
            ).model_dump(by_alias=True)
        },
    ),
]


DOI = Annotated[
    str,
    Field(
        pattern=r"^10[.].+/.+$",
        description="Digital Object Identifier (DOI) matching the format 10.xxxx/xxxx.",
        json_schema_extra={
            "profileValidation": AccessibleCompactURI(default_prefix="doi").model_dump(
                by_alias=True
            )
        },
    ),
]


ORCID = Annotated[
    str,
    Field(
        pattern=r"^[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[X0-9]$",
        description="ORCID digital identifier string matching the format 0000-0000-0000-000X.",
        json_schema_extra={
            "profileValidation": AccessibleCompactURI(
                default_prefix="orcid"
            ).model_dump(by_alias=True)
        },
    ),
]

PubMedId = Annotated[
    str,
    Field(
        pattern=r"^[0-9]{1,20}$",
        title="PubMed Id",
        description="PubMed unique identifier (PMID) of the publication.",
    ),
]

MetaboliteDatabaseId = Annotated[
    CvTermValue,
    Field(
        description="Database identifier (e.g., ChEBI, HMDB, PubChem) for a reported metabolite.",
        json_schema_extra={
            "profileValidation": MANAGED_CHEMICAL_DATABASE_IDENTIFIER_RULE.model_dump(
                by_alias=True
            )
        },
    ),
]

MsTechnologyType = Annotated[
    CvTerm,
    Field(
        description="Controlled Vocabulary (CV) term for mass spectrometry technology type.",
        json_schema_extra={
            "profileValidation": AllowedCvTerms(
                cv_terms=[COMMON_TECHNOLOGY_TYPES["mass spectrometry assay"]]
            ).model_dump(by_alias=True)
        },
    ),
]

ExtendedCharacteristicValues = Annotated[
    list[CvTermKeyValue],
    Field(
        min_length=1,
        description="List of sample characteristic key-value pairs (requiring organism and organism part).",
        json_schema_extra={
            "profileValidation": CheckCvTermKeyValues(
                required_items=[
                    CheckCvTermKeyValue(
                        cv_term_key=COMMON_CHARACTERISTIC_DEFINITIONS["organism"],
                        controls=[MANAGED_CHARACTERISTIC_VALUE_RULES["organism"]],
                        min_value_count=1,
                    ),
                    CheckCvTermKeyValue(
                        cv_term_key=COMMON_CHARACTERISTIC_DEFINITIONS["organism part"],
                        controls=[MANAGED_CHARACTERISTIC_VALUE_RULES["organism part"]],
                        min_value_count=1,
                    ),
                ],
                optional_items=[
                    CheckCvTermKeyValue(
                        cv_term_key=COMMON_CHARACTERISTIC_DEFINITIONS["disease"],
                        controls=[MANAGED_CHARACTERISTIC_VALUE_RULES["disease"]],
                        min_value_count=1,
                    ),
                    CheckCvTermKeyValue(
                        cv_term_key=COMMON_CHARACTERISTIC_DEFINITIONS["cell type"],
                        controls=[MANAGED_CHARACTERISTIC_VALUE_RULES["cell type"]],
                        min_value_count=1,
                    ),
                ],
            ).model_dump(serialize_as_any=True, by_alias=True)
        },
    ),
]

MsAssayType = Annotated[
    CvTerm,
    Field(
        description="Controlled Vocabulary (CV) term for mass spectrometry assay type (e.g., LC-MS, GC-MS).",
        json_schema_extra={
            "profileValidation": AllowedCvTerms(
                cv_terms=list(COMMON_ASSAY_TYPES.values())
            ).model_dump(by_alias=True)
        },
    ),
]


MeasurementType = Annotated[
    CvTerm,
    Field(
        description="Controlled Vocabulary (CV) term for measurement type (e.g., Targeted or Untargeted metabolite profiling).",
        json_schema_extra={
            "profileValidation": AllowedCvTerms(
                cv_terms=list(COMMON_MEASUREMENT_TYPES.values()),
                allowed_placeholder_values=[CvTermPlaceholder()],
            ).model_dump(by_alias=True)
        },
    ),
]


MissingPublicationReason = Annotated[
    CvTerm,
    Field(
        description="Controlled Vocabulary (CV) term specifying reason why publication details are missing.",
        json_schema_extra={
            "profileValidation": AllowedCvTerms(
                cv_terms=list(MISSING_PUBLICATION_REASON.values())
            ).model_dump(by_alias=True)
        },
    ),
]

OmicsType = Annotated[
    CvTerm,
    Field(
        description="Controlled Vocabulary (CV) term for omics domain (e.g., Metabolomics, Lipidomics).",
        json_schema_extra={
            "profileValidation": AllowedCvTerms(
                cv_terms=list(COMMON_OMICS_TYPES.values()),
                allowed_placeholder_values=[CvTermPlaceholder()],
            ).model_dump(by_alias=True)
        },
    ),
]


class ExtendedCvTermKeyValue(CvTermKeyValue):
    """Extended CV term key-value pair supporting custom CV term keys."""

    key: Annotated[
        CvTerm,
        Field(
            description="The Controlled Vocabulary (CV) term key or parameter name.",
            json_schema_extra={
                "profileValidation": AllowAnyCvTerm(
                    allowed_placeholder_values=[CvTermPlaceholder()],
                ).model_dump(by_alias=True)
            },
        ),
    ]


StudyFactors = Annotated[
    list[ExtendedCvTermKeyValue],
    Field(
        min_length=1,
        description="List of experimental study factor key-value pairs varied across samples.",
        json_schema_extra={
            "profileValidation": CheckCvTermKeyValues(
                optional_items=[
                    CheckCvTermKeyValue(
                        cv_term_key=COMMON_CHARACTERISTIC_DEFINITIONS["disease"],
                        controls=[MANAGED_FACTOR_VALUE_RULES["disease"]],
                        min_value_count=1,
                    )
                ]
            ).model_dump(serialize_as_any=True, by_alias=True)
        },
    ),
]

ProtocolType = Annotated[
    CvTerm,
    Field(
        description="Controlled Vocabulary (CV) term specifying the protocol type.",
        json_schema_extra={
            "profileValidation": AllowedCvTerms(
                cv_terms=list(COMMON_PROTOCOLS.values()),
                allowed_placeholder_values=[CvTermPlaceholder()],
            ).model_dump(by_alias=True)
        },
    ),
]


Protocols = Annotated[
    list[AnnouncementProtocol],
    Field(
        description="List of experimental protocols used in sample collection, preparation, or analysis.",
        json_schema_extra={
            "profileValidation": CheckChildCvTermKeyValues(
                conditional_field_name="protocol_type",
                conditional_cv_term=COMMON_PROTOCOLS["mass spectrometry"],
                key_values_field_name="protocol_parameters",
                key_values_control=CheckCvTermKeyValues(
                    required_items=[
                        CheckCvTermKeyValue(
                            cv_term_key=COMMON_PARAMETER_DEFINITIONS[
                                "mass spectrometry instrument"
                            ],
                            controls=[
                                MANAGED_PARAMETER_VALUE_RULES["mass spectrometry"][
                                    "mass spectrometry instrument"
                                ]
                            ],
                        )
                    ]
                ),
            ).model_dump(serialize_as_any=True, by_alias=True)
        },
    ),
]


RawDataFileFormat = Annotated[
    CvTerm,
    Field(
        description="Controlled Vocabulary (CV) term for mass spectrometry raw data file format.",
        json_schema_extra={
            "profileValidation": MANAGED_FILE_FORMAT_RULES[
                "raw data file format"
            ].model_dump(by_alias=True)
        },
    ),
]


CompressionFormat = Annotated[
    CvTerm,
    Field(
        description="Controlled Vocabulary (CV) term for file compression format.",
        json_schema_extra={
            "profileValidation": MANAGED_FILE_FORMAT_RULES[
                "general file format"
            ].model_dump(by_alias=True)
        },
    ),
]

MetadataFileFormat = Annotated[
    CvTerm,
    Field(
        description="Controlled Vocabulary (CV) term for repository metadata file format.",
        json_schema_extra={
            "profileValidation": MANAGED_FILE_FORMAT_RULES[
                "metadata file format"
            ].model_dump(by_alias=True)
        },
    ),
]

ResultFileFormat = Annotated[
    CvTerm,
    Field(
        description="Controlled Vocabulary (CV) term for result file format.",
        json_schema_extra={
            "profileValidation": MANAGED_FILE_FORMAT_RULES[
                "result file format"
            ].model_dump(by_alias=True)
        },
    ),
]

DerivedFileFormat = Annotated[
    CvTerm,
    Field(
        description="Controlled Vocabulary (CV) term for derived data file format.",
        json_schema_extra={
            "profileValidation": MANAGED_FILE_FORMAT_RULES[
                "derived data file format"
            ].model_dump(by_alias=True)
        },
    ),
]

SupplementaryFileFormat = Annotated[
    CvTerm,
    Field(
        description="Controlled Vocabulary (CV) term for supplementary file format.",
        json_schema_extra={
            "profileValidation": MANAGED_FILE_FORMAT_RULES[
                "general file format"
            ].model_dump(by_alias=True)
        },
    ),
]
