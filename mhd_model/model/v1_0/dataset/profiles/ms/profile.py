from typing import Annotated

from pydantic import Field

from mhd_model.model.v1_0.dataset.profiles.base.profile import (
    MhDatasetBaseProfile_v1_0,
)
from mhd_model.shared.model import MhdObjectType


class MhDatasetMsProfile_v1_0(MhDatasetBaseProfile_v1_0):
    type_: Annotated[MhdObjectType, Field(alias="type")] = MhdObjectType("ms-v1-0")
