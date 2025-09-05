from typing import Annotated

from pydantic import Field

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
from mhd_model.shared.model import (
    CvTerm,
    CvTermKeyValue,
    CvTermValue,
    MhdConfigModel,
)
from mhd_model.shared.validation.definitions import (
    AccessibleCompactURI,
    AllowAnyCvTerm,
    AllowedChildrenCvTerms,
    AllowedCvTerms,
    CvTermPlaceholder,
    ParentCvTerm,
)

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

MetabolomicsProtocol = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowedChildrenCvTerms(
                parent_cv_terms=[
                    ParentCvTerm(
                        cv_term=CvTerm(
                            accession="OBI:0000272",
                            source="EFO",
                            name="protocol",
                        ),
                        allow_only_leaf=False,
                    )
                ]
            ).model_dump(by_alias=True)
        }
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
        # json_schema_extra={
        #     "profileValidation": AccessibleCompactURI(default_prefix="pmid").model_dump(
        #         by_alias=True
        #     )
        # },
    ),
]


FactorDefinition = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowAnyCvTerm(
                allowed_placeholder_values=[CvTermPlaceholder(source="", accession="")],
            ).model_dump(by_alias=True)
        }
    ),
]

CvTermOrStr = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowAnyCvTerm(
                allowed_placeholder_values=[CvTermPlaceholder(source="", accession="")],
            ).model_dump(by_alias=True)
        }
    ),
]

ProtocolName = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowedCvTerms(
                cv_terms=list(COMMON_PROTOCOLS.values())
            ).model_dump(by_alias=True)
        }
    ),
]

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
                        controls=[
                            AllowAnyCvTerm(
                                allowed_placeholder_values=[
                                    CvTermPlaceholder(source="", accession="")
                                ]
                            )
                        ],
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
                    allowed_placeholder_values=[
                        CvTermPlaceholder(source="", accession="")
                    ],
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
                            AllowAnyCvTerm(
                                allowed_placeholder_values=[
                                    CvTermPlaceholder(source="", accession="")
                                ]
                            )
                        ],
                        min_value_count=1,
                    )
                ]
            ).model_dump(serialize_as_any=True, by_alias=True)
        },
    ),
]


class Protocol(MhdConfigModel):
    name: Annotated[None | str, Field()] = None
    protocol_type: Annotated[ProtocolName, Field()]
    description: Annotated[None | str, Field()] = None
    protocol_parameters: Annotated[None | list[ExtendedCvTermKeyValue], Field()] = None


Protocols = Annotated[
    list[Protocol],
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
                                            excluded_cv_terms=[
                                                CvTerm(
                                                    source="MS",
                                                    accession="MS:1000491",
                                                    name="Dionex instrument model",
                                                ),
                                                CvTerm(
                                                    source="MS",
                                                    accession="MS:1000488",
                                                    name="Hitachi instrument model",
                                                ),
                                            ],
                                            allow_only_leaf=True,
                                        ),
                                    ]
                                )
                            ],
                        )
                    ]
                ),
            ).model_dump(serialize_as_any=True, by_alias=True)
        }
    ),
]

MeasurementType = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowedCvTerms(
                cv_terms=list(COMMON_MEASUREMENT_TYPES.values())
            ).model_dump(by_alias=True)
        },
    ),
]


OmicsType = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowedCvTerms(
                cv_terms=list(COMMON_OMICS_TYPES.values())
            ).model_dump(by_alias=True)
        },
    ),
]

TechnologyType = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowedCvTerms(
                cv_terms=list(COMMON_TECHNOLOGY_TYPES.values())
            ).model_dump(by_alias=True)
        },
    ),
]


AnalysisType = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowedCvTerms(
                cv_terms=list(COMMON_ASSAY_TYPES.values())
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
