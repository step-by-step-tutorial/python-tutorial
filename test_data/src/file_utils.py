import json
from pathlib import Path
from typing import Any


def list_of_file_names(directory: Path) -> list[str]:
    paths = sorted(Path(directory).glob("*"))
    return [path.name for path in paths]


def read_json_file(path: Path) -> dict[str, Any]:
    file_path = Path(path)
    try:
        raw = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception as error:
        raise Exception(f" Reading JSON file ({file_path}) failed due to: {error}")
    return raw
