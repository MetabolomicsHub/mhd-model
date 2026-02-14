from mhd_model.model.v0_1.rules.managed_cv_terms import COMMON_MISSING_DATA_TERMS
from mhd_model.shared.model import CvTerm
from mhd_model.shared.validation.definitions import (
    AllowedChildrenCvTerms,
    AllowedCvList,
    AllowedCvTerms,
    CvTermPlaceholder,
    ParentCvTerm,
)
from mhd_model.shared.validation.registry import ProfileValidation

MANAGED_CHARACTERISTIC_VALUE_RULES: dict[str, ProfileValidation] = {
    "organism": AllowedCvList(
        source_names=["NCBITAXON", "ENVO", "CHEBI"],
        allowed_other_sources=["wikidata", "ILX"],
    ),
    "organism part": AllowedCvList(
        source_names=["UBERON", "BTO", "NCIT", "CHEBI"],
        allowed_other_sources=["wikidata", "ILX"],
    ),
    "cell type": AllowedCvList(
        source_names=["CL", "CLO"],
        allowed_other_sources=["wikidata", "ILX"],
        allowed_missing_cv_terms=list(COMMON_MISSING_DATA_TERMS.values()),
    ),
    "disease": AllowedCvList(
        source_names=["MONDO", "MP", "SNOMED", "PATO"],
        allowed_other_sources=["wikidata", "ILX"],
        allowed_missing_cv_terms=list(COMMON_MISSING_DATA_TERMS.values()),
    ),
}


MANAGED_FACTOR_VALUE_RULES: dict[str, ProfileValidation] = {
    "disease": AllowedCvList(
        source_names=["MONDO", "MP", "SNOMED", "PATO"],
        allowed_other_sources=["wikidata", "ILX"],
        allowed_missing_cv_terms=list(COMMON_MISSING_DATA_TERMS.values()),
    )
}

MANAGED_PARAMETER_VALUE_RULES: dict[str, dict[str, ProfileValidation]] = {
    "mass spectrometry": {
        "mass spectrometry instrument": AllowedChildrenCvTerms(
            parent_cv_terms=[
                ParentCvTerm(
                    cv_term=CvTerm(
                        source="MS",
                        accession="MS:1000031",
                        name="instrument model",
                    ),
                    excluded_cv_terms=["^.*instrument model"],
                ),
            ],
            allowed_other_sources=["wikidata", "ILX"],
        ),
        "ionization polarity": AllowedCvTerms(
            cv_terms=[
                CvTerm(
                    source="MS",
                    accession="MS:1000076",
                    name="negative polarity acquisition",
                ),
                CvTerm(
                    source="MS",
                    accession="MS:1000077",
                    name="positive polarity acquisition",
                ),
                CvTerm(
                    source="MS",
                    accession="MS:1002833",
                    name="alternating polarity acquisition",
                ),
                CvTerm(
                    source="MS",
                    accession="MS:1003774",
                    name="mixed polarity acquisition",
                ),
            ],
            allowed_other_sources=["wikidata", "ILX"],
        ),
        "ionization type": AllowedChildrenCvTerms(
            parent_cv_terms=[
                ParentCvTerm(
                    cv_term=CvTerm(
                        source="MS",
                        accession="MS:1000008",
                        name="ionization type",
                    ),
                ),
            ],
            allowed_other_sources=["wikidata", "ILX"],
        ),
        "instrument class": AllowedChildrenCvTerms(
            parent_cv_terms=[
                ParentCvTerm(
                    cv_term=CvTerm(
                        source="MS",
                        accession="MS:1003761",
                        name="instrument class",
                    ),
                ),
            ],
            allowed_other_sources=["wikidata", "ILX"],
        ),
        "inlet type": AllowedChildrenCvTerms(
            parent_cv_terms=[
                ParentCvTerm(
                    cv_term=CvTerm(
                        source="MS",
                        accession="MS:1000007",
                        name="inlet type",
                    ),
                ),
            ],
            allowed_other_sources=["wikidata", "ILX"],
        ),
    },
    "chromatography": {
        "chromatography instrument": AllowedChildrenCvTerms(
            parent_cv_terms=[
                ParentCvTerm(
                    cv_term=CvTerm(
                        source="MS",
                        accession="MS:1003737",
                        name="separation system",
                    ),
                ),
            ],
            allowed_other_sources=["wikidata", "ILX"],
        ),
        "chromatography separation": AllowedChildrenCvTerms(
            parent_cv_terms=[
                ParentCvTerm(
                    cv_term=CvTerm(
                        source="MS",
                        accession="MS:1002270",
                        name="chromatography separation",
                    ),
                ),
            ],
            allowed_other_sources=["wikidata", "ILX"],
        ),
    },
}

MANAGED_CHEMICAL_DATABASE_IDENTIFIER_RULE: AllowedChildrenCvTerms = (
    AllowedChildrenCvTerms(
        parent_cv_terms=[
            ParentCvTerm(
                cv_term=CvTerm(
                    accession="CHEMINF:000464",
                    source="CHEMINF",
                    name="chemical database identifier",
                ),
            )
        ],
        allowed_other_sources=["REFMET"],
    )
)

MANAGED_FILE_FORMAT_RULES: dict[str, ProfileValidation] = {
    "raw data file format": AllowedChildrenCvTerms(
        parent_cv_terms=[
            ParentCvTerm(
                cv_term=CvTerm(
                    source="EDAM",
                    accession="EDAM:format_1915",
                    name="Format",
                ),
            ),
            ParentCvTerm(
                cv_term=CvTerm(
                    source="MS",
                    accession="MS:1001459",
                    name="file format",
                ),
            ),
        ],
        list_join_operator="any",
        allowed_placeholder_values=[CvTermPlaceholder()],
    ),
    "derived data file format": AllowedChildrenCvTerms(
        parent_cv_terms=[
            ParentCvTerm(
                cv_term=CvTerm(
                    source="EDAM",
                    accession="EDAM:format_1915",
                    name="Format",
                ),
            ),
            ParentCvTerm(
                cv_term=CvTerm(
                    source="MS",
                    accession="MS:1001459",
                    name="file format",
                ),
            ),
        ],
        list_join_operator="any",
        allowed_placeholder_values=[CvTermPlaceholder()],
    ),
    "metadata file format": AllowedChildrenCvTerms(
        parent_cv_terms=[
            ParentCvTerm(
                cv_term=CvTerm(
                    source="EDAM",
                    accession="EDAM:format_1915",
                    name="Format",
                ),
            ),
            ParentCvTerm(
                cv_term=CvTerm(
                    source="MS",
                    accession="MS:1001459",
                    name="file format",
                ),
            ),
        ],
        list_join_operator="any",
        allowed_placeholder_values=[CvTermPlaceholder()],
    ),
    "result file format": AllowedChildrenCvTerms(
        parent_cv_terms=[
            ParentCvTerm(
                cv_term=CvTerm(
                    source="EDAM",
                    accession="EDAM:format_1915",
                    name="Format",
                ),
            ),
            ParentCvTerm(
                cv_term=CvTerm(
                    source="MS",
                    accession="MS:1001459",
                    name="file format",
                ),
            ),
        ],
        list_join_operator="any",
        allowed_placeholder_values=[CvTermPlaceholder()],
    ),
    "general file format": AllowedChildrenCvTerms(
        parent_cv_terms=[
            ParentCvTerm(
                cv_term=CvTerm(
                    source="EDAM",
                    accession="EDAM:format_1915",
                    name="Format",
                ),
            ),
            ParentCvTerm(
                cv_term=CvTerm(
                    source="MS",
                    accession="MS:1001459",
                    name="file format",
                ),
            ),
        ],
        list_join_operator="any",
        allowed_placeholder_values=[CvTermPlaceholder()],
    ),
}
