import abc
from pathlib import Path

from mhd_model.shared.model import Revision


class BaseMhdConvertor(abc.ABC):
    @abc.abstractmethod
    def convert(
        self,
        reposipory_name: str,
        repository_identifier: str,
        mhd_identifier: None | str,
        mhd_output_folder_path: Path,
        repository_revision: None | Revision = None,
        **kwargs,
    ): ...


class BaseMhdConvertorFactory(abc.ABC):
    @abc.abstractmethod
    def get_convertor(
        self,
        target_mhd_model_schema_uri: str,
        target_mhd_model_profile_uri: str,
    ) -> BaseMhdConvertor: ...
