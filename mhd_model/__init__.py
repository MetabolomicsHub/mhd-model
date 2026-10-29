import pathlib
import sys

__version__ = "v1.0.5"

application_root_path = pathlib.Path(__file__).parent.parent

sys.path.append(str(application_root_path))

__all__ = [
    "convertors",
    "cv_mapping",
    "domain_utils",
    "model",
    "schema_utils",
    "schemas",
    "shared",
    "utils",
    "validation",
]
