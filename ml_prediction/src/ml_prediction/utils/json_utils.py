import json
from pathlib import Path
from typing import Any

JSON_INDENT = 2


def write_json(path: Path, data: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as json_file:
        json.dump(data, json_file, default=lambda value: value.isoformat(), indent=JSON_INDENT)
    return path


def read_json(path: Path) -> Any:
    with Path(path).open(encoding="utf-8") as json_file:
        return json.load(json_file)
