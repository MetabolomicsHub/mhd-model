import abc
import pathlib
from typing import Any


class BaseAnnouncementFileValidator(abc.ABC):
    @abc.abstractmethod
    def validate(self, announcement_file_json: dict[str, Any]) -> list[str]: ...

    @abc.abstractmethod
    def validate_file(self, announcement_file_path: pathlib.Path) -> list[str]: ...


class BaseMhdFileValidator(abc.ABC):
    @abc.abstractmethod
    def validate(self, mhd_file_json: dict[str, Any]) -> list[str]: ...

    @abc.abstractmethod
    def validate_file(self, mhd_file_path: str | pathlib.Path) -> list[str]: ...
