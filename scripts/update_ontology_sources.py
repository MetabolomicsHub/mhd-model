import logging
import re
from pathlib import Path

import httpx2

from mhd_model.domain_utils import (
    OntologySourceReference,
    OntologySourceReferenceTemplate,
)

logger = logging.getLogger(__name__)


def fetch_ols_ontologies() -> OntologySourceReference:
    params = {"lang": "en", "size": 1000}
    headers = {"accept": "application/json"}
    url = "https://www.ebi.ac.uk/ols4/api/ontologies"
    refs: list[OntologySourceReferenceTemplate] = []

    try:
        response = httpx2.get(url, params=params, headers=headers, timeout=20)
        json_data = response.json()
        ontologies = json_data.get("_embedded", {}).get("ontologies")
        ontology_configs = [x.get("config", {}) for x in ontologies]
        for ontology in ontology_configs:
            base_uri = ontology.get("baseUris", None)
            if isinstance(base_uri, str):
                base_uri = [base_uri]
            elif isinstance(base_uri, list) and base_uri:
                base_uri = base_uri[0]
            prefix = base_uri or ontology.get("preferredPrefix", "") or ""
            namespace = ontology.get("namespace", "") or ""
            title = ontology.get("title", "") or ""
            file_location = ontology.get("fileLocation", "") or ""
            file_location = file_location if file_location.startswith("http") else ""
            iri = ontology.get("versionIri", "") or ""
            description = ontology.get("description", "") or ""
            version = ontology.get("version", "") or ""
            source_name = prefix or namespace.upper()
            if not prefix:
                logger.warning(
                    "OLS ontology has no preferred prefix for namespace %s. "
                    "Uppercase version of namespace '%s' will be used.",
                    namespace,
                    namespace.upper(),
                )
            match = re.match(r"[A-Za-z0-9_-]+", source_name)
            if not match:
                logger.warning(
                    "OLS ontology source name has an expected name. "
                    "This ontology source will be ignored. %s",
                    namespace.upper(),
                )
                continue
            refs.append(
                OntologySourceReferenceTemplate(
                    name=source_name.upper(),
                    file=file_location or iri or "",
                    version=str(version) or "",
                    description=title or "",
                    details=description or "",
                    prefix=prefix or "",
                )
            )
    except Exception as ex:
        import traceback

        traceback.print_exc()
        logger.error("Ontologies are not fetched from OLS: %s", ex)

    return OntologySourceReference(ontologies=refs)


def update_ontology_source_json():
    ref = fetch_ols_ontologies()
    file = Path("mhd_model/shared/ontology_sources.json")
    file.write_text(ref.model_dump_json(indent=2))


if __name__ == "__main__":
    update_ontology_source_json()
