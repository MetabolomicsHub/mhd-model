import pathlib
import sys

__version__ = "v0.2.0"

application_root_path = pathlib.Path(__file__).parent.parent

sys.path.append(str(application_root_path))

__all__ = [
    "convertors",
    "domain_utils",
    "model",
    "schema_utils",
    "schemas",
    "shared",
    "utils",
    "validation",
]
