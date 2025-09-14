from typing import Annotated

from pydantic import Field

from mhd_model.model.v0_1.announcement.profiles.base.fields import (
    ExtendedCvTermKeyValue,
)
from mhd_model.model.v0_1.announcement.profiles.base.profile import AnnouncementProtocol
from mhd_model.model.v0_1.announcement.validation.definitions import (
    CheckChildCvTermKeyValues,
    CheckCvTermKeyValue,
    CheckCvTermKeyValues,
)
from mhd_model.model.v0_1.rules.managed_cv_terms import (
    COMMON_ASSAY_TYPES,
    COMMON_PROTOCOLS,
    COMMON_TECHNOLOGY_TYPES,
    REQUIRED_COMMON_PARAMETER_DEFINITIONS,
)
from mhd_model.shared.model import CvTerm, CvTermKeyValue, CvTermValue
from mhd_model.shared.validation.definitions import (
    AllowedChildrenCvTerms,
    AllowedCvList,
    AllowedCvTerms,
    ParentCvTerm,
)

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
                                source_names=["UBERON", "BTO", "NCIT", "SNOMED", "MSIO"]
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
                                source_names=["DOID", "HP", "MP", "SNOMED"],
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
