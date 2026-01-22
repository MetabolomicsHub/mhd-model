from typing import Annotated

from pydantic import Field

from mhd_model.model.v0_1.announcement.profiles.base.profile import AnnouncementProtocol
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
    MISSING_PUBLICATION_REASON,
    REQUIRED_COMMON_PARAMETER_DEFINITIONS,
)
from mhd_model.shared.model import CvTerm, CvTermKeyValue, CvTermValue
from mhd_model.shared.validation.definitions import (
    AccessibleCompactURI,
    AllowAnyCvTerm,
    AllowedChildrenCvTerms,
    AllowedCvList,
    AllowedCvTerms,
    CvTermPlaceholder,
    ParentCvTerm,
)

CvTermOrStr = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowAnyCvTerm(
                allowed_placeholder_values=[CvTermPlaceholder()],
            ).model_dump(by_alias=True)
        }
    ),
]


DOI = Annotated[
    str,
    Field(
        pattern=r"^10[.].+/.+$",
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
    ),
]

MetaboliteDatabaseId = Annotated[
    CvTermValue,
    Field(
        json_schema_extra={
            "profileValidation": AllowedChildrenCvTerms(
                parent_cv_terms=[
                    ParentCvTerm(
                        cv_term=CvTerm(
                            accession="CHEMINF:000464",
                            source="CHEMINF",
                            name="chemical database identifier",
                        ),
                        allow_only_leaf=False,
                        index_cv_terms=False,
                    )
                ],
                allowed_other_sources=["REFMET"],
            ).model_dump(by_alias=True)
        }
    ),
]

MsTechnologyType = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowedCvTerms(
                cv_terms=[COMMON_TECHNOLOGY_TYPES["OBI:0000470"]]
            ).model_dump(by_alias=True)
        },
    ),
]

ExtendedCharacteristicValues = Annotated[
    list[CvTermKeyValue],
    Field(
        min_length=1,
        json_schema_extra={
            "profileValidation": CheckCvTermKeyValues(
                required_items=[
                    CheckCvTermKeyValue(
                        cv_term_key=CvTerm(
                            source="NCIT", accession="NCIT:C14250", name="organism"
                        ),
                        controls=[
                            AllowedCvList(
                                source_names=["ENVO", "NCBITAXON"],
                                allowed_other_sources=["wikidata", "ILX"],
                            )
                        ],
                        min_value_count=1,
                    ),
                    CheckCvTermKeyValue(
                        cv_term_key=CvTerm(
                            source="NCIT",
                            accession="NCIT:C103199",
                            name="organism part",
                        ),
                        controls=[
                            AllowedCvList(
                                source_names=["UBERON", "BTO", "NCIT", "MSIO"]
                            )
                        ],
                        min_value_count=1,
                    ),
                ],
                optional_items=[
                    CheckCvTermKeyValue(
                        cv_term_key=CvTerm(
                            source="EFO", accession="EFO:0000408", name="disease"
                        ),
                        controls=[
                            AllowedCvList(
                                source_names=["MONDO", "MP", "SNOMED"],
                                allowed_other_sources=["wikidata", "ILX"],
                            )
                        ],
                        min_value_count=1,
                    ),
                    CheckCvTermKeyValue(
                        cv_term_key=CvTerm(
                            source="EFO", accession="EFO:0000324", name="cell type"
                        ),
                        controls=[AllowedCvList(source_names=["CL", "CLO"])],
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
        json_schema_extra={
            "profileValidation": AllowedCvTerms(
                cv_terms=list(COMMON_OMICS_TYPES.values()),
                allowed_placeholder_values=[CvTermPlaceholder()],
            ).model_dump(by_alias=True)
        },
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
                                source_names=["MONDO", "MP", "SNOMED"],
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
                            controls=[
                                AllowedChildrenCvTerms(
                                    parent_cv_terms=[
                                        ParentCvTerm(
                                            cv_term=CvTerm(
                                                source="MS",
                                                accession="MS:1000031",
                                                name="instrument model",
                                            ),
                                            allow_only_leaf=True,
                                        ),
                                    ],
                                )
                            ],
                        )
                    ]
                ),
            ).model_dump(serialize_as_any=True, by_alias=True)
        }
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
                            accession="EDAM:format_1915",
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
                            accession="EDAM:format_1915",
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
                            accession="EDAM:format_1915",
                            name="Format",
                        ),
                        index_cv_terms=False,
                    )
                ],
                allowed_placeholder_values=[CvTermPlaceholder()],
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
                            accession="EDAM:format_1915",
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
                            accession="EDAM:format_1915",
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
                            accession="EDAM:format_1915",
                            name="Format",
                        ),
                        index_cv_terms=False,
                    )
                ]
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
                            accession="EDAM:format_1915",
                            name="Format",
                        ),
                        index_cv_terms=False,
                    )
                ]
            ).model_dump(by_alias=True)
        }
    ),
]
