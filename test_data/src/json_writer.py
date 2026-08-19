import json
from collections.abc import Iterable, Mapping
from pathlib import Path


def write_json_rows(output_path: Path, rows: Iterable[Mapping[str, str]]) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(list(rows), file, ensure_ascii=False, indent=2)
        file.write("\n")
    return path
