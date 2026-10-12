from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any


def read_json_file(path: Path) -> dict[str, Any]:
    file_path = Path(path)
    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise FileNotFoundError(f"JSON file not found: {file_path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"JSON file {file_path} is invalid: {error}") from error


def write_json(output_path: Path, rows: Iterable[Mapping[str, str]]) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(list(rows), file, ensure_ascii=False, indent=2)
        file.write("\n")
    return path
