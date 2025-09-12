from typing import Annotated

from pydantic import Field

from mhd_model.model.v0_1.dataset.profiles.base.graph_nodes import Study


class LegacyStudy(Study):
    mhd_identifier: Annotated[None | str, Field()] = None
