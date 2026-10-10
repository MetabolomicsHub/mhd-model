import logging

import bioregistry
from jsonprofile.profile.base import CvTerm as ProfileCvTerm
from jsonprofile.validator.base import (
    CvTermSearch,
)

from mhd_model.shared.base import CvTerm as MhdCvTerm
from mhd_model.shared.validation.cv_term_helper import CvTermHelper
from mhd_model.shared.validation.definitions import ParentCvTerm as MhdParentCvTerm

logger = logging.getLogger(__name__)


class MhdCvTermSearch(CvTermSearch):
    def __init__(self, *args, **kwargs):
        self.cv_term_helper = CvTermHelper()

    def get_iri(self, cv_term: ProfileCvTerm) -> str | None:
        return self.cv_term_helper.get_uri(
            cv_term=MhdCvTerm(
                source=cv_term.cv_label,
                accession=cv_term.cv_accession,
                name=cv_term.name,
            )
        )

    def get_curie(self, cv_term: ProfileCvTerm) -> str | None:
        accession = cv_term.cv_accession
        source = cv_term.cv_accession
        curie = accession
        if accession and (accession.startswith(("http://", "https://"))):
            if source.upper() == "EDAM" and accession:
                curie = f"EDAM:{accession.rstrip('/').split('/')[-1]}"
            else:
                curie = bioregistry.curie_from_iri(accession)
        return curie

    def find_cv_term(
        self,
        source: str,
        accession_or_label: str,
        matched_accession: None | str = None,
        allow_synonym_search: bool = False,
    ) -> None | ProfileCvTerm:
        cv_term = self.cv_term_helper.find_cv_term(
            source=source,
            accession_or_label=accession_or_label,
            matched_accession=matched_accession,
            allow_synonym_search=allow_synonym_search,
        )
        if cv_term:
            return ProfileCvTerm(
                cv_label=cv_term.source,
                cv_accession=cv_term.accession,
                name=cv_term.name,
            )
        return None

    def check_cv_term(
        self,
        cv_term: ProfileCvTerm,
        parent_cv_term: None | ProfileCvTerm = None,
        allow_synonym_search: bool = False,
    ) -> tuple[bool, str]:
        parent = None
        if parent_cv_term:
            parent = MhdParentCvTerm(
                cv_term=MhdCvTerm(
                    source=parent_cv_term.cv_label,
                    accession=parent_cv_term.cv_accession,
                    name=parent_cv_term.name,
                )
            )
        success, message = self.cv_term_helper.check_cv_term(
            cv_term=MhdCvTerm(
                source=cv_term.cv_label,
                accession=cv_term.cv_accession,
                name=cv_term.name,
            ),
            parent_cv_term=parent,
            allow_synonym_search=allow_synonym_search,
        )
        return success, message

    def find_cv_term_with_accession(
        self, source: str, accession: str
    ) -> tuple[ProfileCvTerm, list[str]]:
        cv_term, alternatives = self.cv_term_helper.find_cv_term_with_accession(
            source=source, accession=accession
        )
        if cv_term:
            profile_cv_term = ProfileCvTerm(
                cv_label=cv_term.source,
                cv_accession=cv_term.accession,
                name=cv_term.name,
            )
            return profile_cv_term, alternatives
        return cv_term, alternatives
