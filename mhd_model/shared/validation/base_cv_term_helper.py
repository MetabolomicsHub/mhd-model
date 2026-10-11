import abc
import logging

from mhd_model.shared.base import BaseParentCvTerm, CvTerm

logger = logging.getLogger(__name__)


class BaseCvTermHelper(abc.ABC):
    @abc.abstractmethod
    def check_cv_term(
        self,
        cv_term: CvTerm,
        parent_cv_term: None | BaseParentCvTerm = None,
        allow_synonym_search: bool = False,
    ) -> tuple[bool, str]: ...

    @abc.abstractmethod
    def get_uri(self, cv_term: CvTerm) -> str | None: ...

    @abc.abstractmethod
    def find_cv_term(
        self,
        source: str,
        accession_or_label: str,
        matched_accession: None | str = None,
        allow_synonym_search: bool = False,
    ) -> None | CvTerm: ...

    @abc.abstractmethod
    def find_cv_term_with_accession(
        self, source: str, accession: str
    ) -> tuple[CvTerm, list[str]]: ...
