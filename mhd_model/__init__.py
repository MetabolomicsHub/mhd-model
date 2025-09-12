import pathlib
import sys

from . import (
    convertors,
    domain_utils,
    model,
    schema_utils,
    schemas,
    shared,
    utils,
)

__version__ = "v0.1.7"

application_root_path = pathlib.Path(__file__).parent.parent

sys.path.append(str(application_root_path))

__all__ = [
    "domain_utils",
    "schema_utils",
    "utils",
    "schemas",
    "shared",
    "model",
    "convertors",
]
