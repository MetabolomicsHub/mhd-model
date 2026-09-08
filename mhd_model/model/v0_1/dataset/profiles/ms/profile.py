from typing import Annotated

from pydantic import Field

from mhd_model.model.v0_1.dataset.profiles.base.base import (
    MhdObjectType,
)
from mhd_model.model.v0_1.dataset.profiles.base.profile import (
    MhDatasetBaseProfile,
)


class MhDatasetMsProfile(MhDatasetBaseProfile):
    type_: Annotated[MhdObjectType, Field(frozen=True, alias="type")] = MhdObjectType(
        "ms-dataset"
    )
