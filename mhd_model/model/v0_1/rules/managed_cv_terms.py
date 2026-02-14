from typing import OrderedDict

from mhd_model.shared.model import CvTerm

COMMON_MISSING_DATA_TERMS: dict[str, CvTerm] = {
    "not applicable": CvTerm(
        source="NCIT",
        accession="NCIT:C48660",
        name="Not Applicable",
    ),
    "not available": CvTerm(
        source="NCIT",
        accession="NCIT:C126101",
        name="Not Available",
    ),
    "masked data": CvTerm(
        source="NCIT",
        accession="NCIT:C150904",
        name="Masked Data",
    ),
}

MISSING_PUBLICATION_REASON: dict[str, CvTerm] = {
    "no publication": CvTerm(
        source="MS",
        accession="MS:1002853",
        name="Dataset with no associated published manuscript",
    ),
    "pending publication": CvTerm(
        source="MS",
        accession="MS:1002858",
        name="Dataset with its publication pending",
    ),
}

COMMON_TECHNOLOGY_TYPES: dict[str, CvTerm] = {
    "mass spectrometry assay": CvTerm(
        source="OBI",
        accession="OBI:0000470",
        name="mass spectrometry assay",
    ),
    # TODO: Will be enabled in future
    # "OBI:0000623": CvTerm(
    #     source="OBI",
    #     accession="OBI:0000623",
    #     name="NMR spectroscopy assay",
    # ),
}

COMMON_MEASUREMENT_TYPES: dict[str, CvTerm] = {
    "untargeted": CvTerm(
        source="MS",
        accession="MS:1003904",
        name="untargeted analysis",
    ),
    "targeted": CvTerm(
        source="MS",
        accession="MS:1003905",
        name="targeted analysis",
    ),
    "semi-targeted": CvTerm(
        source="MS",
        accession="MS:1003906",
        name="semi-targeted analysis",
    ),
}

COMMON_ASSAY_TYPES: dict[str, CvTerm] = {
    "lc-ms": CvTerm(
        source="OBI",
        accession="OBI:0003097",
        name="liquid chromatography mass spectrometry assay",
    ),
    "gc-ms": CvTerm(
        source="OBI",
        accession="OBI:0003110",
        name="gas chromatography mass spectrometry assay",
    ),
    "ce-ms": CvTerm(
        source="OBI",
        accession="OBI:0003741",
        name="capillary electrophoresis mass spectrometry assay",
    ),
    "ms": CvTerm(
        source="OBI",
        accession="OBI:0000470",
        name="mass spectrometry assay",
    ),
    # TODO: Will be enabled in future
    # "OBI:0000623": CvTerm(
    #     source="OBI",
    #     accession="OBI:0000623",
    #     name="NMR spectroscopy assay",
    # ),
}

COMMON_OMICS_TYPES = {
    "metabolomics": CvTerm(
        source="EDAM",
        accession="EDAM:topic_3172",
        name="Metabolomics",
    ),
    "lipidomics": CvTerm(
        source="EDAM",
        accession="EDAM:topic_0153",
        name="Lipidomics",
    ),
    "fluxomics": CvTerm(
        source="EDAM",
        accession="EDAM:topic_3955",
        name="Fluxomics",
    ),
    # TODO: Update once EDAM ontolgy is updated on OLS
    "exposomics": CvTerm(
        source="wikidata",
        accession="wikidata:Q115452339",
        name="exposomics",
    ),
}


COMMON_PROTOCOLS: dict[str, CvTerm] = {
    "mass spectrometry": CvTerm(
        source="CHMO",
        accession="CHMO:0000470",
        name="mass spectrometry",
    ),
    "chromatography": CvTerm(
        source="CHMO",
        accession="CHMO:0001000",
        name="chromatography",
    ),
    "sample collection": CvTerm(
        source="EFO",
        accession="EFO:0005518",
        name="sample collection protocol",
    ),
    "treatment": CvTerm(
        source="EFO",
        accession="EFO:0003969",
        name="treatment protocol",
    ),
    "sample preparation": CvTerm(
        source="MS",
        accession="MS:1000831",
        name="sample preparation",
    ),
}

COMMON_CHARACTERISTIC_DEFINITION_ENFORCEMENT_LEVELS: dict[str, dict[str, CvTerm]] = {
    "required": {
        "organism": CvTerm(source="NCIT", accession="NCIT:C14250", name="organism"),
        "organism part": CvTerm(
            source="NCIT", accession="NCIT:C103199", name="organism part"
        ),
        "disease": CvTerm(source="EFO", accession="EFO:0000408", name="disease"),
        "cell type": CvTerm(source="EFO", accession="EFO:0000324", name="cell type"),
    },
    "recommended": {
        # TODO: will be defined in future
        # "geographical location": CvTerm(
        #     source="EFO", accession="GAZ:00000448", name="geographical location"
        # ),
        # "collection date": CvTerm(
        #     source="NCIT", accession="NCIT:C81286", name="collection date"
        # ),
    },
    "optional": {},
}

COMMON_CHARACTERISTIC_DEFINITIONS: dict[str, CvTerm] = {}

for _, terms in COMMON_CHARACTERISTIC_DEFINITION_ENFORCEMENT_LEVELS.items():
    for label, term in terms.items():
        COMMON_CHARACTERISTIC_DEFINITIONS[label] = term


COMMON_STUDY_FACTOR_DEFINITION_ENFORCEMENT_LEVELS: dict[str, CvTerm] = {
    "required": {},
    "recommended": {},
    "optional": {
        "disease": CvTerm(source="EFO", accession="EFO:0000408", name="disease"),
    },
}


COMMON_STUDY_FACTOR_DEFINITIONS: dict[str, CvTerm] = {}

for _, terms in COMMON_STUDY_FACTOR_DEFINITION_ENFORCEMENT_LEVELS.items():
    for label, term in terms.items():
        COMMON_STUDY_FACTOR_DEFINITIONS[label] = term

COMMON_PARAMETER_ENFORCEMENT_LEVELS: dict[str, dict[str, dict[str, CvTerm]]] = {
    "mass spectrometry": {
        "required": {
            "mass spectrometry instrument": CvTerm(
                source="MSIO",
                accession="MSIO:0000171",
                name="mass spectrometry instrument",
            ),
            # TODO: update after MS ontology is updated
            "acquisition polarity": CvTerm(
                source="wikidata",
                accession="wikidata:Q138265353",
                name="acquisition polarity",
            ),
        },
        "recommended": {},
        "optional": {
            "ionization type": CvTerm(
                source="MS", accession="MS:1000008", name="ionization type"
            ),
            "instrument class": CvTerm(
                source="MS", accession="MS:1003761", name="instrument class"
            ),
            "inlet type": CvTerm(
                source="MS", accession="MS:1000007", name="inlet type"
            ),
        },
    },
    "chromatography": {
        "required": {},
        "recommended": {
            "chromatography instrument": CvTerm(
                source="OBI", accession="OBI:0000485", name="chromatography instrument"
            ),
            "chromatography column": CvTerm(
                source="OBI", accession="OBI:0000038", name="chromatography column"
            ),
        },
        "optional": {
            "chromatography separation": CvTerm(
                source="MS", accession="MS:1002270", name="chromatography separation"
            ),
            "solvent": CvTerm(source="CHEBI", accession="CHEBI:46787", name="solvent"),
            "chromatographic additive": CvTerm(
                source="CHEBI",
                accession="CHEBI:747205",
                name="chromatographic additive",
            ),
        },
    },
}
COMMON_PROTOCOL_PARAMETER_MAPPINGS: OrderedDict[str, CvTerm] = OrderedDict()
COMMON_PARAMETER_DEFINITIONS: OrderedDict[str, CvTerm] = OrderedDict()
for protocol, enforcements in COMMON_PARAMETER_ENFORCEMENT_LEVELS.items():
    if protocol not in COMMON_PROTOCOL_PARAMETER_MAPPINGS:
        COMMON_PROTOCOL_PARAMETER_MAPPINGS[protocol] = OrderedDict()
    for enforcement_level, terms in enforcements.items():
        for label, term in terms.items():
            COMMON_PARAMETER_DEFINITIONS[label] = term
            COMMON_PROTOCOL_PARAMETER_MAPPINGS[protocol][label] = term


MANAGED_CV_TERM_OBJECTS: set[str] = {
    "characteristic-type",
    "characteristic-value",
    "metabolite-identifier",
    "data-provider",
    "descriptor",
    "factor-type",
    "factor-value",
    "parameter-type",
    "parameter-value",
    "protocol-type",
}


# COMMON_PARAMETER_DEFINITIONS: dict[str, CvTerm] = {
#     ##------------------------ Mass Spectrometry -------------------------------
#     "mass spectrometry instrument": CvTerm(
#         source="MSIO", accession="MSIO:0000171", name="mass spectrometry instrument"
#     ),
#     # TODO: update after MS ontology is updated
#     "acquisition polarity": CvTerm(
#         source="wikidata", accession="wikidata:Q138265353", name="acquisition polarity"
#     ),
#     "ionization type": CvTerm(
#         source="MS", accession="MS:1000008", name="ionization type"
#     ),
#     "instrument class": CvTerm(
#         source="MS", accession="MS:1003761", name="instrument class"
#     ),
#     "inlet type": CvTerm(source="MS", accession="MS:1000007", name="inlet type"),
#     ##--------------------------- Chromatography ----------------------------------
#     "chromatography instrument": CvTerm(
#         source="OBI", accession="OBI:0000485", name="chromatography instrument"
#     ),
#     "chromatography column": CvTerm(
#         source="OBI", accession="OBI:0000038", name="chromatography column"
#     ),
#     "chromatography separation": CvTerm(
#         source="MS", accession="MS:1002270", name="chromatography separation"
#     ),
#     "solvent": CvTerm(source="CHEBI", accession="CHEBI:46787", name="solvent"),
#     "chromatographic additive": CvTerm(
#         source="CHEBI", accession="CHEBI:747205", name="chromatographic additive"
#     ),
# }


# REQUIRED_PARAMETER_DEFINITIONS = {
#     "CHMO:0000470": {
#         "MSIO:0000171": REQUIRED_COMMON_PARAMETER_DEFINITIONS["MSIO:0000171"],
#     },
#     "CHMO:0001000": {
#         "MSIO:0000171": REQUIRED_COMMON_PARAMETER_DEFINITIONS["MSIO:0000171"],
#     },
# }

# COMMON_PROTOCOL_PARAMETERS = {
#     "CHMO:0000470": {
#         "MS:1000465": COMMON_PARAMETER_DEFINITIONS["MS:1000465"],
#         # "MTBLS:50020": COMMON_PARAMETER_DEFINITIONS["MTBLS:50020"],
#         "MSIO:0000171": COMMON_PARAMETER_DEFINITIONS["MSIO:0000171"],
#         "CHMO:0000960": COMMON_PARAMETER_DEFINITIONS["CHMO:0000960"],
#         "OBI:0000345": COMMON_PARAMETER_DEFINITIONS["OBI:0000345"],
#     },
#     "CHMO:0001000": {
#         "OBI:0000485": COMMON_PARAMETER_DEFINITIONS["OBI:0000485"],
#         # "MTBLS:50001": COMMON_PARAMETER_DEFINITIONS["MTBLS:50001"],
#         # "MTBLS:50002": COMMON_PARAMETER_DEFINITIONS["MTBLS:50002"],
#         # "MTBLS:50003": COMMON_PARAMETER_DEFINITIONS["MTBLS:50003"],
#         # "MTBLS:50004": COMMON_PARAMETER_DEFINITIONS["MTBLS:50004"],
#     },
# }


# # TODO Add all of them
# assay_technique_protocols = {
#     "CE-MS": [
#         "Capillary Electrophoresis",
#         "Mass spectrometry",
#     ],
#     "DI-MS": [
#         "Direct infusion",
#         "Mass spectrometry",
#     ],
#     "FIA-MS": [
#         "Flow Injection Analysis",
#         "Mass spectrometry",
#     ],
#     "GC-FID": [
#         "Chromatography",
#     ],
#     "GC-MS": [
#         "Chromatography",
#         "Mass spectrometry",
#     ],
#     "GCxGC-MS": [
#         "Sample collection",
#         "Extraction",
#         "Chromatography",
#         "Mass spectrometry",
#     ],
#     "LC-DAD": [
#         "Sample collection",
#         "Extraction",
#         "Chromatography",
#         "Data transformation",
#         "Metabolite identification",
#     ],
#     "LC-MS": [
#         "Sample collection",
#         "Extraction",
#         "Chromatography",
#         "Mass spectrometry",
#         "Data transformation",
#         "Metabolite identification",
#     ],
#     "MALDI-MS": [
#         "Sample collection",
#         "Extraction",
#         "Mass spectrometry",
#         "Data transformation",
#         "Metabolite identification",
#     ],
#     "MS": [
#         "Sample collection",
#         "Extraction",
#         "Mass spectrometry",
#         "Data transformation",
#         "Metabolite identification",
#     ],
# }
