from typing import Annotated

from pydantic import Field

from mhd_model.model.v0_1.announcement.validation.definitions import (
    CheckCvTermKeyValue,
    CheckCvTermKeyValues,
)
from mhd_model.model.v0_1.rules.managed_cv_terms import (
    COMMON_ASSAY_TYPES,
    COMMON_TECHNOLOGY_TYPES,
)
from mhd_model.shared.model import CvTerm, CvTermKeyValue
from mhd_model.shared.validation.definitions import AllowedCvList, AllowedCvTerms

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

MsAnalysisType = Annotated[
    CvTerm,
    Field(
        json_schema_extra={
            "profileValidation": AllowedCvTerms(
                cv_terms=list(COMMON_ASSAY_TYPES.values())
            ).model_dump(by_alias=True)
        },
    ),
]
