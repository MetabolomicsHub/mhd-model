import pathlib
import sys

<<<<<<< HEAD
__version__ = "v0.1.8"
=======

__version__ = "v0.1.10"
>>>>>>> 582ab5a6f38d964d8479c4756fbd617b22d36477

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
