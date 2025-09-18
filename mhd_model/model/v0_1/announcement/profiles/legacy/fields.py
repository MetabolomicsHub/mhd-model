from typing import Annotated

from pydantic import Field

from mhd_model.model.v0_1.announcement.profiles.base.profile import (
    AnnouncementProtocol,
)
from mhd_model.model.v0_1.announcement.validation.definitions import (
    CheckChildCvTermKeyValues,
    CheckCvTermKeyValue,
    CheckCvTermKeyValues,
)
from mhd_model.model.v0_1.rules.managed_cv_terms import (
    COMMON_ASSAY_TYPES,
    COMMON_MEASUREMENT_TYPES,
    COMMON_OMICS_TYPES,
    COMMON_PROTOCOLS,
    COMMON_TECHNOLOGY_TYPES,
    REQUIRED_COMMON_PARAMETER_DEFINITIONS,
)
from mhd_model.shared.model import CvTerm, CvTermKeyValue
from mhd_model.shared.validation.definitions import (
    AllowAnyCvTerm,
    AllowedChildrenCvTerms,
    AllowedCvList,
    AllowedCvTerms,
    CvTermPlaceholder,
    ParentCvTerm,
)

CharacteristicValues = Annotated[
    list[CvTermKeyValue],
    Field(
        json_schema_extra={
            "profileValidation": CheckCvTermKeyValues(
                required_items=[
                    CheckCvTermKeyValue(
                        cv_term_key=CvTerm(
                            source="NCIT", accession="NCIT:C14250", name="organism"
                        ),
                        controls=[],
                        min_value_count=1,
                    ),
                ]
            ).model_dump(serialize_as_any=True, by_alias=True)
        }
    ),
]


class ExtendedCvTermKeyValue(CvTermKeyValue):
    key: Annotated[
        CvTerm,
        Field(
            json_schema_extra={
                "profileValidation": AllowAnyCvTerm(
                    allowed_placeholder_values=[CvTermPlaceholder()],
                ).model_dump(by_alias=True)
            }
        ),
    ]


StudyFactors = Annotated[
    list[ExtendedCvTermKeyValue],
    Field(
        min_length=1,
        json_schema_extra={
            "profileValidation": CheckCvTermKeyValues(
                optional_items=[
                    CheckCvTermKeyValue(
                        cv_term_key=CvTerm(
                            source="EFO", accession="EFO:0000408", name="disease"
                        ),
                        controls=[
                            AllowedCvList(
                                source_names=["DOID", "HP", "MP", "SNOMED"],
                                allowed_placeholder_values=[CvTermPlaceholder()],
                                allowed_other_sources=["wikidata", "ILX"],
                            )
                        ],
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
        json_schema_extra={
            "profileValidation": AllowedCvTerms(
                cv_terms=list(COMMON_PROTOCOLS.values()),
                allowed_placeholder_values=[CvTermPlaceholder()],
            ).model_dump(by_alias=True)
        }
    ),
]

Protocols = Annotated[
    list[AnnouncementProtocol],
    Field(
        json_schema_extra={
            "profileValidation": CheckChildCvTermKeyValues(
                conditional_field_name="protocol_type",
                conditional_cv_term=COMMON_PROTOCOLS["CHMO:0000470"],
                key_values_field_name="protocol_parameters",
                key_values_control=CheckCvTermKeyValues(
                    required_items=[
                        CheckCvTermKeyValue(
                            cv_term_key=REQUIRED_COMMON_PARAMETER_DEFINITIONS[
                                "MSIO:0000171"
                            ],
                            controls=[],
                        )
                    ]
                ),
            ).model_dump(serialize_as_any=True, by_alias=True)
        },
    ),
]

MeasurementType = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowedCvTerms(
                cv_terms=list(COMMON_MEASUREMENT_TYPES.values()),
                allowed_placeholder_values=[CvTermPlaceholder()],
            ).model_dump(by_alias=True)
        },
    ),
]

OmicsType = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowedCvTerms(
                cv_terms=list(COMMON_OMICS_TYPES.values()),
                allowed_placeholder_values=[CvTermPlaceholder()],
            ).model_dump(by_alias=True)
        },
    ),
]

TechnologyType = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowedCvTerms(
                cv_terms=list(COMMON_TECHNOLOGY_TYPES.values()),
                allowed_placeholder_values=[CvTermPlaceholder()],
            ).model_dump(by_alias=True)
        },
    ),
]


AssayType = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowedCvTerms(
                cv_terms=list(COMMON_ASSAY_TYPES.values()),
                allowed_placeholder_values=[CvTermPlaceholder()],
            ).model_dump(by_alias=True)
        },
    ),
]

RawDataFileFormat = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowedChildrenCvTerms(
                parent_cv_terms=[
                    ParentCvTerm(
                        cv_term=CvTerm(
                            source="EDAM",
                            accession="EDAM:1915",
                            name="Format",
                        ),
                        index_cv_terms=False,
                    ),
                    ParentCvTerm(
                        cv_term=CvTerm(
                            source="MS",
                            accession="MS:1000560",
                            name="mass spectrometer file format",
                        ),
                    ),
                ],
            ).model_dump(by_alias=True)
        }
    ),
]


CompressionFormat = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowedChildrenCvTerms(
                parent_cv_terms=[
                    ParentCvTerm(
                        cv_term=CvTerm(
                            source="EDAM",
                            accession="EDAM:1915",
                            name="Format",
                        ),
                        index_cv_terms=False,
                    )
                ]
            ).model_dump(by_alias=True)
        }
    ),
]

MetadataFileFormat = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowedChildrenCvTerms(
                parent_cv_terms=[
                    ParentCvTerm(
                        cv_term=CvTerm(
                            source="EDAM",
                            accession="EDAM:1915",
                            name="Format",
                        ),
                        index_cv_terms=False,
                    )
                ]
            ).model_dump(by_alias=True)
        }
    ),
]

ResultFileFormat = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowedChildrenCvTerms(
                parent_cv_terms=[
                    ParentCvTerm(
                        cv_term=CvTerm(
                            source="EDAM",
                            accession="EDAM:1915",
                            name="Format",
                        ),
                        index_cv_terms=False,
                    )
                ]
            ).model_dump(by_alias=True)
        }
    ),
]

DerivedFileFormat = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowedChildrenCvTerms(
                parent_cv_terms=[
                    ParentCvTerm(
                        cv_term=CvTerm(
                            source="EDAM",
                            accession="EDAM:1915",
                            name="Format",
                        ),
                        index_cv_terms=False,
                        allow_only_leaf=False,
                    ),
                ]
            ).model_dump(by_alias=True)
        }
    ),
]

SupplementaryFileFormat = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowedChildrenCvTerms(
                parent_cv_terms=[
                    ParentCvTerm(
                        cv_term=CvTerm(
                            source="EDAM",
                            accession="EDAM:1915",
                            name="Format",
                        ),
                        index_cv_terms=False,
                    )
                ]
            ).model_dump(by_alias=True)
        }
    ),
]
