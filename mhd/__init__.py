import pathlib
import sys

__version__ = "v3.3.0"

application_root_path = pathlib.Path(__file__).parent.parent

sys.path.append(str(application_root_path))
