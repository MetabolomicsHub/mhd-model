import json
import logging
import pathlib
import sys
from typing import Any

logger = logging.getLogger(__name__)


def load_json(file: str) -> dict[str, Any]:
    with pathlib.Path(file).open("r") as f:
        json_file = json.load(f)
    return json_file


def json_path(field_path: list[int | str]) -> str:
    return ".".join([x if isinstance(x, str) else f"[{x}]" for x in field_path])


def setup_basic_logging_config(level: int = logging.INFO):
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] %(levelname)s "
        "[%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%d/%b/%Y %H:%M:%S",
        stream=sys.stdout,
    )

    logging.getLogger("httpx2").setLevel(logging.WARNING)
