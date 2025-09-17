import logging

import httpx

from mhd_model.shared.model import CvDefinition

logger = logging.getLogger(__name__)


def search_ontology_definition(ontology_name: str) -> None | CvDefinition:
    if not ontology_name:
        return None
    try:
        url = "https://www.ebi.ac.uk/ols4/api/v2/ontologies" + ontology_name.lower()
        response = httpx.get(url, timeout=2)
        response.raise_for_status()
        json_response = response.json()
        base_uri = json_response.get("baseUri", [])

        return CvDefinition(
            name=json_response.get("description", ""),
            uri=json_response.get("iri", ""),
            prefix=base_uri[0] if base_uri else "",
            label=json_response.get("preferredPrefix", "").upper(),
        )
    except Exception as e:
        logger.error(
            "Error while fetching ontology definition from OLS: '%s' - %s",
            ontology_name,
            e,
        )
        return None
