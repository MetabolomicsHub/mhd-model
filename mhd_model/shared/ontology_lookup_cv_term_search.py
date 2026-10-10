import logging

from jsonprofile.profile.base import CvTerm as ProfileCvTerm
from jsonprofile.validator.base import (
    CvTermSearch,
)
from ontology_lookup import OntologyLookupService
from ontology_lookup.models import (
    CurieResolutionResponse,
    IriResolutionResponse,
    SearchTermSummary,
    TermResponse,
)

logger = logging.getLogger(__name__)


class OntologyLookupCvTermSearch(CvTermSearch):
    def __init__(self, db_path: str, *args, **kwargs):
        self.svc = OntologyLookupService(db_path=db_path)

    def get_iri(self, cv_term: ProfileCvTerm) -> str | None:
        if cv_term.cv_accession.startswith(("http://", "https://")):
            return cv_term.cv_accession
        result: None | IriResolutionResponse = self.svc.find_iri(
            curie=cv_term.cv_accession, ontology=cv_term.cv_label
        )

        if not result:
            return None
        return result.iri or None

    def get_curie(self, cv_term: ProfileCvTerm) -> str | None:
        if not cv_term.cv_accession.startswith(("http://", "https://")):
            return cv_term.cv_accession
        result: CurieResolutionResponse = self.svc.find_curie(
            iri=cv_term.cv_accession, ontology=cv_term.cv_label
        )

        if not result:
            return None
        return result.curie or None

    def find_cv_term(
        self,
        source: str,
        accession_or_label: str,
        matched_accession: None | str = None,
        allow_synonym_search: bool = False,
    ) -> None | ProfileCvTerm:
        result = None
        if matched_accession:
            result: TermResponse = self.svc.get_term_by_accession(
                ontology=source, accession=matched_accession
            )
        if result:
            return ProfileCvTerm(
                cv_label=result.ontology, cv_accession=result.curie, name=result.label
            )
        result: TermResponse = self.svc.get_term_by_accession(
            ontology=source, accession=accession_or_label
        )
        if result:
            return ProfileCvTerm(
                cv_label=result.ontology, cv_accession=result.curie, name=result.label
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
            return ProfileCvTerm(
                cv_label=result.ontology, cv_accession=result.curie, name=result.label
            )
        return None

    def check_cv_term(
        self,
        cv_term: ProfileCvTerm,
        parent_cv_term: None | ProfileCvTerm = None,
        allow_synonym_search: bool = False,
    ) -> tuple[bool, str]:
        ontology = cv_term.cv_label
        if not cv_term.cv_label:
            if ":" in cv_term.cv_accession:
                ontology = cv_term.cv_label.split(":", maxsplit=1)[0]
            else:
                return (
                    False,
                    f"Invalid ontology for {cv_term.name}",
                )
        if parent_cv_term:
            result = self.svc.search_by_label(
                ontology=ontology,
                label_or_synonym=cv_term.name,
                parent_curie=parent_cv_term.cv_accession,
                search_in_synonyms=allow_synonym_search,
            )
            if result:
                return (
                    True,
                    f"{cv_term.cv_accession} is child of {parent_cv_term.cv_accession}",
                )
            return (
                False,
                f"{cv_term.cv_accession} is not child of {parent_cv_term.cv_accession}",
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
                f"{cv_term.cv_accession} is found result with label {result[0].label} ",
            )
        return (
            False,
            f"{cv_term.cv_accession} '{cv_term.name}' is not found in ontology {cv_term.cv_label}",
        )

    def find_cv_term_with_accession(
        self, source: str, accession: str
    ) -> tuple[ProfileCvTerm | None, list[str] | None]:
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
            profile_cv_term = ProfileCvTerm(
                cv_label=result.ontology,
                cv_accession=result.curie,
                name=result.label,
            )
            return profile_cv_term, result.synonyms or []
        return None, None
