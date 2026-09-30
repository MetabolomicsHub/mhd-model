import json
import logging
import pathlib
from typing import Any

logger = logging.getLogger(__name__)


def load_json(file: str) -> dict[str, Any]:
    with pathlib.Path(file).open("r") as f:
        json_file = json.load(f)
    return json_file


def json_path(field_path: list[int | str]) -> str:
    return ".".join([x if isinstance(x, str) else f"[{x}]" for x in field_path])
