from mhd_model.shared.model import CvTerm

MANAGED_CV_TERM_OBJECTS = {
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

COMMON_TECHNOLOGY_TYPES = {
    "OBI:0000470": CvTerm(
        source="OBI",
        accession="OBI:0000470",
        name="mass spectrometry assay",
    ),
    "OBI:0000623": CvTerm(
        source="OBI",
        accession="OBI:0000623",
        name="NMR spectroscopy assay",
    ),
}

COMMON_ASSAY_TYPES = {
    "OBI:0003097S": CvTerm(
        source="OBI",
        accession="OBI:0003097",
        name="liquid chromatography mass spectrometry assay",
    ),
    "OBI:0003110": CvTerm(
        source="OBI",
        accession="OBI:0003110",
        name="gas chromatography mass spectrometry assay",
    ),
    "OBI:0000470": CvTerm(
        source="OBI",
        accession="OBI:0000470",
        name="mass spectrometry assay",
    ),
    "OBI:0000623": CvTerm(
        source="OBI",
        accession="OBI:0000623",
        name="NMR spectroscopy assay",
    ),
    # CE-MS
    # DI-MS
    # FIA-MS
    # GCxGC-MS
    # MALDI-MS
    # MSImaging
    # GC-FID
    # LC-DAD
    # MRImaging
}

COMMON_MEASUREMENT_TYPES = {
    "MSIO:0000100": CvTerm(
        source="MSIO",
        accession="MSIO:0000100",
        name="targeted metabolite profiling",
    ),
    "MSIO:0000101": CvTerm(
        source="MSIO",
        accession="MSIO:0000101",
        name="untargeted metabolite profiling",
    ),
    # TODO others?
}

COMMON_OMICS_TYPES = {
    "EDAM:3172": CvTerm(
        source="EDAM",
        accession="EDAM:3172",
        name="Metabolomics",
    ),
    "EDAM:0153": CvTerm(
        source="EDAM",
        accession="EDAM:0153",
        name="Lipidomics",
    ),
    "EDAM:3955": CvTerm(
        source="EDAM",
        accession="EDAM:3955",
        name="Fluxomics",
    ),
    # TODO others?
}

MISSING_PUBLICATION_REASON = {
    "MS:1002853": CvTerm(
        source="MS",
        accession="MS:1002853",
        name="no associated published manuscript",
    ),
    "MS:1002858": CvTerm(
        source="MS",
        accession="MS:1002858",
        name="Dataset with its publication pending",
    ),
}

COMMON_CHARACTERISTIC_DEFINITIONS = {
    "NCIT:C14250": CvTerm(source="NCIT", accession="NCIT:C14250", name="organism"),
    "NCIT:C103199": CvTerm(
        source="NCIT", accession="NCIT:C103199", name="organism part"
    ),
    "EFO:0000408": CvTerm(source="EFO", accession="EFO:0000408", name="disease"),
    "EFO:0000324": CvTerm(source="EFO", accession="EFO:0000324", name="cell type"),
    # "GAZ:00000448": CvTerm(
    #     source="EFO", accession="GAZ:00000448", name="geographical location"
    # ),
}


REQUIRED_CHARACTERISTIC_DEFINITIONS = {
    "NCIT:C14250": COMMON_CHARACTERISTIC_DEFINITIONS["NCIT:C14250"],
    "NCIT:C103199": COMMON_CHARACTERISTIC_DEFINITIONS["NCIT:C103199"],
}

COMMON_STUDY_FACTOR_DEFINITIONS = {
    "EFO:0000408": CvTerm(source="EFO", accession="EFO:0000408", name="disease"),
}


REQUIRED_COMMON_PARAMETER_DEFINITIONS = {
    "MSIO:0000171": CvTerm(
        source="MSIO", accession="MSIO:0000171", name="mass spectrometry instrument"
    ),
    "OBI:0000485": CvTerm(
        source="OBI", accession="OBI:0000485", name="chromatography instrument"
    ),
}

COMMON_PARAMETER_DEFINITIONS = REQUIRED_COMMON_PARAMETER_DEFINITIONS.copy()
COMMON_PARAMETER_DEFINITIONS.update(
    {
        "MS:1000465": CvTerm(source="MS", accession="MS:1000465", name="scan polarity"),
        "OBI:0000521": CvTerm(
            source="OBI", accession="OBI:0000521", name="flame ionization detector"
        ),
        "CHMO:0002503": CvTerm(
            source="CHMO", accession="CHMO:0002503", name="diode array detector"
        ),
        "OBI:0001132": CvTerm(
            source="OBI",
            accession="OBI:0001132",
            name="capillary electrophoresis instrument",
        ),
        "OBI:0000345": CvTerm(
            source="OBI", accession="OBI:0000345", name="mass analyzer"
        ),
        "CHMO:0000960": CvTerm(
            source="CHMO", accession="CHMO:0000960", name="ion source"
        ),
        "MTBLS:50001": CvTerm(
            source="MTBLS",
            accession="MTBLS:50001",
            name="column model",
        ),
        "MTBLS:50002": CvTerm(
            source="MTBLS",
            accession="MTBLS:50002",
            name="column type",
        ),
        "MTBLS:50003": CvTerm(
            source="MTBLS",
            accession="MTBLS:50003",
            name="guard column",
        ),
        "MTBLS:50004": CvTerm(
            source="MTBLS",
            accession="MTBLS:50004",
            name="autosampler model",
        ),
        "MTBLS:50010": CvTerm(
            source="MTBLS",
            accession="MTBLS:50010",
            name="post extraction",
        ),
        "MTBLS:50011": CvTerm(
            source="MTBLS",
            accession="MTBLS:50011",
            name="derivatization",
        ),
        "MTBLS:50020": CvTerm(
            source="MTBLS",
            accession="MTBLS:50020",
            name="scan m/z range",
        ),
        "MTBLS:50021": CvTerm(
            source="MTBLS",
            accession="MTBLS:50021",
            name="fia instrument",
        ),
        # column model
        # column type
        # scan m/z range
        # flow injection analysis (FIA) instrument
    }
)

REQUIRED_PARAMETER_DEFINITIONS = {
    "LC-MS": {
        "CHMO:0000470": {
            "MSIO:0000171": REQUIRED_COMMON_PARAMETER_DEFINITIONS["MSIO:0000171"],
        }
    },
    "GC-MS": {
        "CHMO:0000470": {
            "MSIO:0000171": REQUIRED_COMMON_PARAMETER_DEFINITIONS["MSIO:0000171"],
        }
    },
    "CE-MS": {
        "CHMO:0000470": {
            "MSIO:0000171": REQUIRED_COMMON_PARAMETER_DEFINITIONS["MSIO:0000171"],
        }
    },
    "DI-MS": {
        "CHMO:0000470": {
            "MSIO:0000171": REQUIRED_COMMON_PARAMETER_DEFINITIONS["MSIO:0000171"],
        }
    },
    "FIA-MS": {
        "CHMO:0000470": {
            "MSIO:0000171": REQUIRED_COMMON_PARAMETER_DEFINITIONS["MSIO:0000171"],
        }
    },
    "GCxGC-MS": {
        "CHMO:0000470": {
            "MSIO:0000171": REQUIRED_COMMON_PARAMETER_DEFINITIONS["MSIO:0000171"],
        }
    },
    ####### OTHERS ######
    # MR Imaging, LC-DAD, GC-FID, NMR
}

COMMON_PROTOCOL_PARAMETERS = {
    "CHMO:0000470": {
        "MS:1000465": COMMON_PARAMETER_DEFINITIONS["MS:1000465"],
        "MTBLS:50020": COMMON_PARAMETER_DEFINITIONS["MTBLS:50020"],
        "MSIO:0000171": COMMON_PARAMETER_DEFINITIONS["MSIO:0000171"],
        "CHMO:0000960": COMMON_PARAMETER_DEFINITIONS["CHMO:0000960"],
        "OBI:0000345": COMMON_PARAMETER_DEFINITIONS["OBI:0000345"],
    },
    "CHMO:0001000": {
        "OBI:0000485": COMMON_PARAMETER_DEFINITIONS["OBI:0000485"],
        "MTBLS:50001": COMMON_PARAMETER_DEFINITIONS["MTBLS:50001"],
        "MTBLS:50002": COMMON_PARAMETER_DEFINITIONS["MTBLS:50002"],
        "MTBLS:50003": COMMON_PARAMETER_DEFINITIONS["MTBLS:50003"],
        "MTBLS:50004": COMMON_PARAMETER_DEFINITIONS["MTBLS:50004"],
    },
}

COMMON_PROTOCOLS = {
    "EFO:0005518": CvTerm(
        source="EFO",
        accession="EFO:0005518",
        name="sample collection protocol",
    ),
    "MS:1000831": CvTerm(
        source="MS",
        accession="MS:1000831",
        name="sample preparation",
    ),
    "CHMO:0000470": CvTerm(
        source="CHMO",
        accession="CHMO:0000470",
        name="mass spectrometry",
    ),
    "OBI:0200000": CvTerm(
        source="OBI",
        accession="OBI:0200000",
        name="data transform",
    ),
    "MI:2131": CvTerm(
        source="MI",
        accession="MI:2131",
        name="metabolite identification",
    ),
    "CHMO:0001000": CvTerm(
        source="CHMO",
        accession="CHMO:0001000",
        name="chromatography",
    ),
    "EFO:0003969": CvTerm(
        source="EFO",
        accession="EFO:0003969",
        name="treatment protocol",
    ),
    "CHMO:0001024": CvTerm(
        source="CHMO",
        accession="CHMO:0001024",
        name="capillary electrophoresis",
    ),
    "MS:1000058": CvTerm(
        source="MS",
        accession="MS:1000058",
        name="flow injection analysis",
    ),
    ###### DI-MS ######
    # Direct infusion
    ###### SPE-IMS-MS ######
    # Solid-Phase Extraction Ion Mobility Spectrometry
    ###### MSImaging ######
    # Preparation
    # Histology
    ###### MRImaging ######
    # Magnetic resonance imaging
    # In vivo magnetic resonance spectroscopy
    # In vivo magnetic resonance assay
    ###### NMR ######
    # NMR sample
    # NMR spectroscopy
    # NMR assay
}

# TODO Add all of them
assay_technique_protocols = {
    "CE-MS": [
        "Capillary Electrophoresis",
        "Mass spectrometry",
    ],
    "DI-MS": [
        "Direct infusion",
        "Mass spectrometry",
    ],
    "FIA-MS": [
        "Flow Injection Analysis",
        "Mass spectrometry",
    ],
    "GC-FID": [
        "Chromatography",
    ],
    "GC-MS": [
        "Chromatography",
        "Mass spectrometry",
    ],
    "GCxGC-MS": [
        "Sample collection",
        "Extraction",
        "Chromatography",
        "Mass spectrometry",
    ],
    "LC-DAD": [
        "Sample collection",
        "Extraction",
        "Chromatography",
        "Data transformation",
        "Metabolite identification",
    ],
    "LC-MS": [
        "Sample collection",
        "Extraction",
        "Chromatography",
        "Mass spectrometry",
        "Data transformation",
        "Metabolite identification",
    ],
    "MALDI-MS": [
        "Sample collection",
        "Extraction",
        "Mass spectrometry",
        "Data transformation",
        "Metabolite identification",
    ],
    "MRImaging": [
        "Sample collection",
        "Magnetic resonance imaging",
        "In vivo magnetic resonance spectroscopy",
        "In vivo magnetic resonance assay",
        "Data transformation",
        "Metabolite identification",
    ],
    "MS": [
        "Sample collection",
        "Extraction",
        "Mass spectrometry",
        "Data transformation",
        "Metabolite identification",
    ],
    "MSImaging": [
        "Sample collection",
        "Preparation",
        "Mass spectrometry",
        "Histology",
        "Data transformation",
        "Metabolite identification",
    ],
    "NMR": [
        "Sample collection",
        "Extraction",
        "NMR sample",
        "NMR spectroscopy",
        "NMR assay",
        "Data transformation",
        "Metabolite identification",
    ],
    "SPE-IMS-MS": [
        "Sample collection",
        "Extraction",
        "Solid-Phase Extraction Ion Mobility Spectrometry",
        "Mass spectrometry",
        "Data transformation",
        "Metabolite identification",
    ],
    "TD-GC-MS": [
        "Sample collection",
        "Extraction",
        "Chromatography",
        "Mass spectrometry",
        "Data transformation",
        "Metabolite identification",
    ],
}
