from mhd_model.shared.model import CvDefinition

CONTROLLED_CV_DEFINITIONS = {
    "MTBLS": CvDefinition(
        label="MTBLS",
        name="MetaboLights Controlled Vocabulary",
        uri="https://raw.githubusercontent.com/EBI-Metabolights/MtblsWS-Py/refs/heads/main/resources/Metabolights.owl",
        prefix="http://www.ebi.ac.uk/metabolights/ontology/MTBLS_",
    ),
    "BTO": CvDefinition(
        label="BTO",
        name="The BRENDA Tissue Ontology (BTO)",
        uri="http://purl.obolibrary.org/obo/bto.owl",
        prefix="http://purl.obolibrary.org/obo/BTO_",
    ),
    "CHEMINF": CvDefinition(
        label="CHEMINF",
        name="chemical information ontology (cheminf) - information entities about chemical entities",
        uri="http://semanticchemistry.github.io/semanticchemistry/ontology/cheminf.owl",
        prefix="http://semanticscience.org/resource/CHEMINF_",
    ),
    "DOID": CvDefinition(
        label="DOID",
        name="Human Disease Ontology",
        uri="http://purl.obolibrary.org/obo/doid.owl",
        prefix="http://purl.obolibrary.org/obo/DOID_",
    ),
    "EDAM": CvDefinition(
        label="EDAM",
        name="The ontology of data analysis and management",
        uri="http://edamontology.org",
        prefix="http://edamontology.org/format_",
    ),
    "ENVO": CvDefinition(
        label="ENVO",
        name="The Environment Ontology",
        uri="http://purl.obolibrary.org/obo/envo.owl",
        prefix="http://purl.obolibrary.org/obo/ENVO_",
    ),
    "EFO": CvDefinition(
        label="EFO",
        name="Experimental Factor Ontology",
        uri="http://www.ebi.ac.uk/efo/efo.owl",
        prefix="http://www.ebi.ac.uk/efo/EFO_",
    ),
    "MS": CvDefinition(
        label="MS",
        name="MS",
        uri="http://purl.obolibrary.org/obo/ms.owl",
        prefix="http://purl.obolibrary.org/obo/MS_",
    ),
    "MSIO": CvDefinition(
        label="MSIO",
        name="Metabolomics Standards Initiative Ontology (MSIO)",
        uri="http://purl.obolibrary.org/obo/msio.owl",
        prefix="http://purl.obolibrary.org/obo/MSIO_",
    ),
    "NCBITAXON": CvDefinition(
        label="NCBITAXON",
        name="National Center for Biotechnology Information (NCBI) Organismal Classification",
        uri="http://purl.obolibrary.org/obo/ncbitaxon.owl",
        prefix="http://purl.obolibrary.org/obo/NCBITaxon_",
        alternative_labels=["NCBITaxon"],
        alternative_prefixes=["http://purl.bioontology.org/ontology/NCBITAXON/"],
    ),
    "NCIT": CvDefinition(
        label="NCIT",
        name="NCI Thesaurus OBO Edition",
        uri="http://purl.obolibrary.org/obo/ncit.owl",
        prefix="http://purl.obolibrary.org/obo/NCIT_",
    ),
    "OBI": CvDefinition(
        label="OBI",
        name="Ontology for Biomedical Investigations",
        uri="http://purl.obolibrary.org/obo/obi.owl",
        prefix="http://purl.obolibrary.org/obo/OBI_",
    ),
    "SWO": CvDefinition(
        label="SWO",
        name="Software Ontology",
        uri="http://www.ebi.ac.uk/swo/swo.owl",
        prefix="http://www.ebi.ac.uk/swo/SWO_",
    ),
}


OTHER_CONTROLLED_CV_DEFINITIONS = {
    "DOI": CvDefinition(
        label="doi",
        name="Digital Object Identifier",
        uri="https://www.doi.org",
        prefix="https://www.doi.org/",
        alternative_labels=["DOI"],
        alternative_prefixes=["http://www.doi.org/"],
    ),
    "ORCID": CvDefinition(
        label="orcid",
        name="Digital Object Identifier",
        uri="https://orcid.org",
        prefix="https://orcid.org/",
        alternative_labels=["ORCID"],
        alternative_prefixes=["http://orcid.org/"],
    ),
    "PMID": CvDefinition(
        label="PMID",
        name="PubMed",
        uri="https://pubmed.ncbi.nlm.nih.gov",
        prefix="https://pubmed.ncbi.nlm.nih.gov/",
        alternative_labels=["pmid"],
        alternative_prefixes=["http://pubmed.ncbi.nlm.nih.gov/"],
    ),
    "WIKIDATA": CvDefinition(
        label="WIKIDATA",
        name="Wikidata",
        uri="https://www.wikidata.org/wiki",
        prefix="https://www.wikidata.org/wiki/",
        alternative_labels=["wikidata"],
        alternative_prefixes=["http://www.wikidata.org/wiki/"],
    ),
    "WoRMS": CvDefinition(
        label="WoRMS",
        name="World Register of Marine Species",
        uri="https://www.marinespecies.org",
        prefix="https://www.marinespecies.org/aphia.php?p=taxdetails&id=",
        alternative_labels=["WORMS", "worms"],
        alternative_prefixes=[
            "http://www.marinespecies.org/aphia.php?p=taxdetails&id="
        ],
    ),
}
