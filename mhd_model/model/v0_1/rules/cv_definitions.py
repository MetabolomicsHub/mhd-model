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
    "CHEBI": CvDefinition(
        label="CHEBI",
        name="Chemical Entities of Biological Interest",
        uri="http://purl.obolibrary.org/obo/chebi.owl",
        prefix="http://purl.obolibrary.org/obo/CHEBI_",
    ),
    "CHEMINF": CvDefinition(
        label="CHEMINF",
        name="chemical information ontology (cheminf) - information entities about chemical entities",
        uri="http://semanticchemistry.github.io/semanticchemistry/ontology/cheminf.owl",
        prefix="http://semanticscience.org/resource/CHEMINF_",
    ),
    "CHMO": CvDefinition(
        label="CHMO",
        name="Chemical Methods Ontology",
        uri="http://purl.obolibrary.org/obo/chmo.owl",
        prefix="http://purl.obolibrary.org/obo/CHMO_",
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
        alternative_prefixes=[
            "http://edamontology.org/operation_",
            "http://edamontology.org/topic_, http://edamontology.org/data_",
        ],
    ),
    "EFO": CvDefinition(
        label="EFO",
        name="Experimental Factor Ontology",
        uri="http://www.ebi.ac.uk/efo/efo.owl",
        prefix="http://www.ebi.ac.uk/efo/EFO_",
    ),
    "ENVO": CvDefinition(
        label="ENVO",
        name="The Environment Ontology",
        uri="http://purl.obolibrary.org/obo/envo.owl",
        prefix="http://purl.obolibrary.org/obo/ENVO_",
    ),
    "GO": CvDefinition(
        label="GO",
        name="Gene Ontology",
        uri="http://purl.obolibrary.org/obo/go/extensions/go-plus.owl",
        prefix="http://purl.obolibrary.org/obo/GO_",
    ),
    "MI": CvDefinition(
        label="MI",
        name="Molecular Interactions Controlled Vocabulary",
        uri=" http://purl.obolibrary.org/obo/mi.owl",
        prefix="http://purl.obolibrary.org/obo/MI_",
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
        label="DOI",
        name="Digital Object Identifier",
        uri="https://www.doi.org",
        prefix="https://www.doi.org/",
        alternative_labels=["doi"],
        alternative_prefixes=["http://www.doi.org/"],
    ),
    "ORCID": CvDefinition(
        label="ORCID",
        name="Digital Object Identifier",
        uri="https://orcid.org",
        prefix="https://orcid.org/",
        alternative_labels=["orcid"],
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
    "REFMET": CvDefinition(
        label="REFMET",
        name="Reference list of Metabolite names",
        uri="https://www.metabolomicsworkbench.org/databases/refmet/refmet_details.php",
        prefix="https://www.metabolomicsworkbench.org/databases/refmet/refmet_details.php?REFMET_ID=",
        alternative_labels=["refmet", "REFMET"],
    ),
    "ILX": CvDefinition(
        label="ILX",
        name="InterLex Identifier",
        uri="http://www.interlex.org",
        prefix="http://uri.interlex.org/user/ilx_",
        alternative_labels=["ilx"],
        alternative_prefixes=["http://uri.interlex.org/user/ilx_"],
    ),
    "WORMS": CvDefinition(
        label="WORMS",
        name="World Register of Marine Species",
        uri="https://www.marinespecies.org",
        prefix="https://www.marinespecies.org/aphia.php?p=taxdetails&id=",
        alternative_labels=["WORMS", "worms", "WoRMS"],
        alternative_prefixes=[
            "http://www.marinespecies.org/aphia.php?p=taxdetails&id="
        ],
    ),
}
