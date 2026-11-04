"""CV term helper backed by the MHD ontology lookup REST API."""

import json
import logging
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import urlopen

from mhd_model.shared.base import BaseParentCvTerm, CvTerm
from mhd_model.shared.model import CvDefinition
from mhd_model.shared.validation.base_cv_term_helper import BaseCvTermHelper

logger = logging.getLogger(__name__)


class MhdOntologyLookupCvTermHelper(BaseCvTermHelper):
    """Use the ontology lookup endpoints hosted by an MHD server.

    ``base_mhd_server_url`` is the server origin or a URL already ending in
    ``/ontology-lookup``. The latter is useful when the router is mounted at a
    non-default path.
    """

    def __init__(self, base_mhd_server_url: str, timeout: float = 10.0):
        self.base_mhd_server_url = base_mhd_server_url.rstrip("/")
        self.timeout = timeout
        if self.base_mhd_server_url.endswith("/ontology-lookup"):
            self.api_base_url = self.base_mhd_server_url
        else:
            self.api_base_url = f"{self.base_mhd_server_url}/ontology-lookup"

    def _get(self, path: str, params: dict | None = None):
        url = f"{self.api_base_url}{path}"
        if params:
            url = f"{url}?{urlencode(params, doseq=True)}"
        try:
            with urlopen(url, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            if error.code == 404:
                return None
            logger.warning("Ontology lookup request failed (%s): %s", error.code, url)
            raise
        except (URLError, TimeoutError):
            logger.exception("Could not reach ontology lookup service at %s", url)
            raise

    @staticmethod
    def _term(record: dict | None) -> CvTerm | None:
        if not record:
            return None
        return CvTerm(
            source=record.get("ontology"),
            accession=record.get("curie"),
            name=record.get("label"),
        )

    @staticmethod
    def _is_obsolete(record: dict) -> bool:
        tags = record.get("tags") or {}
        return bool(tags.get("obsolete"))

    def get_ontology_definition(self, ontology_name: str) -> CvDefinition | None:
        result = self._get(f"/ontologies/{quote(ontology_name, safe='')}")
        if not result:
            return None
        return CvDefinition(
            name=result.get("name"),
            uri=result.get("source_uri"),
            prefix=result.get("prefix") or None,
            label=result.get("ontology"),
            version=result.get("version") or None,
        )

    def check_cv_term(
        self,
        cv_term: CvTerm,
        parent_cv_term: BaseParentCvTerm | None = None,
        allow_synonym_search: bool = False,
        allow_obsoletes: bool = True,
    ) -> tuple[bool, str]:
        ontology = cv_term.source
        if not ontology and ":" in cv_term.accession:
            ontology = cv_term.accession.split(":", maxsplit=1)[0]
        if not ontology:
            return False, f"Invalid ontology for {cv_term.name}"

        params = {
            "q": cv_term.name,
            "ontology": ontology,
            "search_in_synonyms": allow_synonym_search,
            "limit": 1,
        }
        if not allow_obsoletes:
            params["ignore_obsolete"] = True
        if parent_cv_term and parent_cv_term.cv_term:
            params["parent_curie"] = parent_cv_term.cv_term.accession
        results = self._get("/search", params) or []
        if not allow_obsoletes:
            results = [result for result in results if not self._is_obsolete(result)]
        valid = bool(results)
        if parent_cv_term and parent_cv_term.cv_term:
            parent_accession = parent_cv_term.cv_term.accession
            if valid:
                return True, f"{cv_term.accession} is child of {parent_accession}"
            return False, f"{cv_term.accession} is not child of {parent_accession}"
        if valid:
            return (
                True,
                f"{cv_term.accession} is found result with label {results[0].get('label')}",
            )
        return (
            False,
            f"{cv_term.accession} '{cv_term.name}' is not found in ontology {ontology}",
        )

    def get_uri(self, cv_term: CvTerm) -> str | None:
        if cv_term.accession.startswith(("http://", "https://")):
            return cv_term.accession
        result = self._get(
            "/resolve/iri",
            {"curie": cv_term.accession, "ontology": cv_term.source},
        )
        return result.get("iri") if result else None

    def get_curie(self, cv_term: CvTerm) -> str | None:
        if not cv_term.accession.startswith(("http://", "https://")):
            return cv_term.accession
        result = self._get(
            "/resolve/curie",
            {"iri": cv_term.accession, "ontology": cv_term.source},
        )
        return result.get("curie") if result else None

    def find_cv_term(
        self,
        source: str,
        accession_or_label: str,
        matched_accession: str | None = None,
        allow_synonym_search: bool = False,
        allow_obsoletes: bool = True,
    ) -> CvTerm | None:
        for accession in (matched_accession, accession_or_label):
            if not accession:
                continue
            result = self._get(
                f"/ontologies/{quote(source, safe='')}/terms/{quote(accession, safe=':/')}"
            )
            if result and (allow_obsoletes or not self._is_obsolete(result)):
                return self._term(result)

        if allow_synonym_search:
            results = (
                self._get(
                    "/search",
                    {
                        "q": accession_or_label,
                        "ontology": source,
                        "search_in_synonyms": True,
                        "limit": 50,
                    },
                )
                or []
            )
            results = [
                result
                for result in results
                if allow_obsoletes or not self._is_obsolete(result)
            ]
            if results:
                return self._term(results[0])
        else:
            result = self._get(
                "/search/exact", {"ontology": source, "label": accession_or_label}
            )
            if result and (allow_obsoletes or not self._is_obsolete(result)):
                return self._term(result)
        return None

    def find_cv_term_with_accession(
        self, source: str, accession: str, allow_obsoletes: bool = True
    ) -> tuple[CvTerm | None, list[str] | None]:
        ontology = source or (
            accession.split(":", maxsplit=1)[0]
            if ":" in accession and not accession.startswith(("http://", "https://"))
            else None
        )
        if not ontology:
            return None, []
        result = self._get(
            f"/ontologies/{quote(ontology, safe='')}/terms/{quote(accession, safe=':/')}"
        )
        if not result:
            return None, None
        if not allow_obsoletes and self._is_obsolete(result):
            return None, None
        return self._term(result), result.get("synonyms") or []
