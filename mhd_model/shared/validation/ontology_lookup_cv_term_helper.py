import logging

from ontology_lookup import OntologyLookupService
from ontology_lookup.models import (
    IriResolutionResponse,
    SearchTermSummary,
    TermResponse,
)

from mhd_model.shared.base import CvTerm
from mhd_model.shared.validation.cv_term_helper import (
    BaseCvTermHelper,
)
from mhd_model.shared.validation.definitions import ParentCvTerm

logger = logging.getLogger(__name__)


class OntologyLookupCvTermHelper(BaseCvTermHelper):
    def __init__(self, db_path: str, *args, **kwargs):
        self.svc = OntologyLookupService(db_path=db_path)

    def check_cv_term(
        self,
        cv_term: CvTerm,
        parent_cv_term: None | ParentCvTerm = None,
        allow_synonym_search: bool = False,
    ) -> tuple[bool, str]:
        ontology = cv_term.source
        if not cv_term.source:
            if ":" in cv_term.accession:
                ontology = cv_term.source.split(":", maxsplit=1)[0]
            else:
                return (
                    False,
                    f"Invalid ontology for {cv_term.name}",
                )
        if parent_cv_term and parent_cv_term.cv_term:
            result = self.svc.search_by_label(
                ontology=ontology,
                label_or_synonym=cv_term.name,
                parent_curie=parent_cv_term.cv_term.accession,
                search_in_synonyms=allow_synonym_search,
                connection=self.conn,
            )
            if result:
                return (
                    True,
                    f"{cv_term.accession} is child of {parent_cv_term.cv_term.accession}",
                )
            return (
                False,
                f"{cv_term.accession} is not child of {parent_cv_term.cv_term.accession}",
            )
        result: list[SearchTermSummary] = self.svc.search_by_label(
            ontology=ontology,
            label_or_synonym=cv_term.name,
            search_in_synonyms=allow_synonym_search,
            limit=1,
        )
        if result:
            return (
                True,
                f"{cv_term.accession} is found result with label {result[0].label} ",
            )
        return (
            False,
            f"{cv_term.accession} '{cv_term.name}' is not found in ontology {cv_term.source}",
        )

    def get_uri(self, cv_term: CvTerm) -> str | None:
        if cv_term.accession.startswith(("http://", "https://")):
            return cv_term.accession
        result: None | IriResolutionResponse = self.svc.find_iri(
            curie=cv_term.accession, ontology=cv_term.source
        )
        if not result:
            return None
        return result.iri or None

    def find_cv_term(
        self,
        source: str,
        accession_or_label: str,
        matched_accession: None | str = None,
        allow_synonym_search: bool = False,
    ) -> None | CvTerm:
        result = None
        if matched_accession:
            result: TermResponse = self.svc.get_term_by_accession(
                ontology=source, accession=matched_accession
            )
        if result:
            return CvTerm(
                source=result.ontology, accession=result.curie, name=result.label
            )
        result: TermResponse = self.svc.get_term_by_accession(
            ontology=source, accession=accession_or_label
        )
        if result:
            return CvTerm(
                source=result.ontology, accession=result.curie, name=result.label
            )
        if allow_synonym_search:
            result: list[SearchTermSummary] = self.svc.search_by_label(
                ontology=source, label_or_synonym=accession_or_label
            )
            if result:
                result = result[0]
        else:
            result: TermResponse = self.svc.get_term_by_exact_label(
                ontology=source, label=accession_or_label
            )
        if result:
            return CvTerm(
                source=result.ontology, accession=result.curie, name=result.label
            )
        return None

    def find_cv_term_with_accession(
        self, source: str, accession: str
    ) -> tuple[CvTerm, list[str]]:
        ontology = source
        if not ontology:
            if ":" in accession:
                ontology = accession.split(":", maxsplit=1)[0]
            else:
                return None, []

        result: None | TermResponse = self.svc.get_term_by_accession(
            ontology=ontology, accession=accession
        )
        if result:
            profile_cv_term = CvTerm(
                source=result.ontology,
                accession=result.curie,
                name=result.label,
            )
            return profile_cv_term, result.synonyms or []
        return None, None
