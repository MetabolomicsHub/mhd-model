from pydantic import Field
from typing_extensions import Annotated

from mhd_model.model.v1_0.dataset.profiles.base.base import (
    MhdObjectType,
)
from mhd_model.model.v1_0.dataset.profiles.base.profile import (
    MhDatasetBaseProfile,
)


class MhDatasetLegacyProfile(MhDatasetBaseProfile):
    type_: Annotated[MhdObjectType, Field(frozen=True, alias="type")] = MhdObjectType(
        "legacy-dataset"
    )
