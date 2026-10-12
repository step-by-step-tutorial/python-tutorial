import csv
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any


def resolve_path(base_dir: Path, value: str | Path) -> Path:
    """Return value as an absolute path; a relative value is resolved against base_dir."""
    path = Path(value)
    return path if path.is_absolute() else (base_dir / path).resolve()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def read_tsv(path: Path) -> Iterator[list[str]]:
    """Yield the rows of a tab-separated file without quote handling, as used by the GeoNames dumps."""
    with path.open("r", encoding="utf-8", newline="") as file:
        yield from csv.reader(file, delimiter="\t", quoting=csv.QUOTE_NONE)
