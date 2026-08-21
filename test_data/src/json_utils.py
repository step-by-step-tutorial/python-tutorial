from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any


def read_json_file(path: Path) -> dict[str, Any]:
    file_path = Path(path)
    try:
        raw = json.loads(file_path.read_text(encoding="utf-8"))
    except Exception as error:
        raise Exception(f"Reading JSON file ({file_path}) failed due to: {error}")

    return raw


def write_json(output_path: Path, rows: Iterable[Mapping[str, str]]) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(list(rows), file, ensure_ascii=False, indent=2)
        file.write("\n")
    return path
