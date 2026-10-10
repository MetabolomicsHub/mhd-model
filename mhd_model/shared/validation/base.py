import abc
import pathlib
from typing import Any

from mhd_model.shared.model import MhdModelValidationContext


class BaseAnnouncementFileValidator(abc.ABC):
    @abc.abstractmethod
    def validate(
        self,
        announcement_file_json: dict[str, Any],
        ontology_lookup_file_path: None | str = None,
    ) -> list[str]: ...

    @abc.abstractmethod
    def validate_file(
        self,
        announcement_file_path: pathlib.Path,
        ontology_lookup_file_path: None | str = None,
    ) -> list[str]: ...


class BaseMhdFileValidator(abc.ABC):
    @abc.abstractmethod
    def validate(
        self,
        mhd_file_json: dict[str, Any],
        ontology_lookup_file_path: None | str = None,
        mhd_model_validation_context: None | MhdModelValidationContext = None,
    ) -> list[str]: ...

    @abc.abstractmethod
    def validate_file(
        self,
        mhd_file_path: str | pathlib.Path,
        ontology_lookup_file_path: None | str = None,
        mhd_model_validation_context: None | MhdModelValidationContext = None,
    ) -> list[str]: ...
