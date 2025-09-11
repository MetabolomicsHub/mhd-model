from mhd_model.shared.model import CvTerm

PREDEFINED_CV_TERMS: dict[str, dict[str, CvTerm]] = {
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
    "OBI:0000366": CvTerm(
        source="OBI",
        accession="OBI:0000366",
        name="metabolite profiling assay",
    ),
    "OBI:0000485": CvTerm(
        source="OBI", accession="OBI:0000485", name="chromatography instrument"
    ),
    "OBI:0000521": CvTerm(
        source="OBI", accession="OBI:0000521", name="flame ionization detector"
    ),
    "OBI:0000345": CvTerm(source="OBI", accession="OBI:0000345", name="mass analyzer"),
    "OBI:0001132": CvTerm(
        source="OBI",
        accession="OBI:0001132",
        name="capillary electrophoresis instrument",
    ),
    "OBI:0200000": CvTerm(
        source="OBI",
        accession="OBI:0200000",
        name="data transform",
    ),
    "MS:1000031": CvTerm(
        source="MS",
        accession="MS:1000031",
        name="instrument model",
    ),
    "MS:1000560": CvTerm(
        source="MS",
        accession="MS:1000560",
        name="mass spectrometer file format",
    ),
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
    "NCIT:C14250": CvTerm(source="NCIT", accession="NCIT:C14250", name="organism"),
    "NCIT:C103199": CvTerm(
        source="NCIT", accession="NCIT:C103199", name="organism part"
    ),
    "EFO:0000324": CvTerm(source="EFO", accession="EFO:0000324", name="cell type"),
    "EFO:0000408": CvTerm(source="EFO", accession="EFO:0000408", name="disease"),
    "CHMO:0000470": CvTerm(
        source="CHMO",
        accession="CHMO:0000470",
        name="mass spectrometry",
    ),
    "CHMO:0001000": CvTerm(
        source="CHMO",
        accession="CHMO:0001000",
        name="chromatography",
    ),
    "MSIO:0000171": CvTerm(
        source="MSIO", accession="MSIO:0000171", name="mass spectrometry instrument"
    ),
}
