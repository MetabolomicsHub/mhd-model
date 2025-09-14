from typing import Annotated

from pydantic import Field

from mhd_model.model.v0_1.rules.managed_cv_terms import (
    COMMON_ASSAY_TYPES,
    COMMON_MEASUREMENT_TYPES,
    COMMON_OMICS_TYPES,
    COMMON_PROTOCOLS,
    COMMON_TECHNOLOGY_TYPES,
    MISSING_PUBLICATION_REASON,
)
from mhd_model.shared.model import (
    CvTerm,
    CvTermKeyValue,
    CvTermValue,
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
                allowed_placeholder_values=[CvTermPlaceholder()],
            ).model_dump(by_alias=True)
        }
    ),
]

FactorDefinition = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowAnyCvTerm(
                allowed_placeholder_values=[CvTermPlaceholder()],
            ).model_dump(by_alias=True)
        }
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
