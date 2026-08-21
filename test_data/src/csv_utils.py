from __future__ import annotations

import csv
from collections.abc import Iterable, Sequence, Callable
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from file_utils import absolute_project_path
from validation_utils import require_or_raise_map, require_not_blank


def write_csv(output_path: Path, headers: Sequence[str], rows: Iterable[Mapping[str, str]]) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(headers))
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def read_csv_file(path: str, consumer: Callable[[dict[str, str]], None]) -> int:
    path = absolute_project_path(path)
    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                consumer(row)
    except Exception:
        raise Exception(f"Reading CSV file failed due to: {path}")


def extract_map_from_csv(path: str, key_column: str, value_column: str) -> Mapping[str, str]:
    absolute_path = absolute_project_path(path)
    mapping: dict[str, str] = {}
    read_csv_file(str(absolute_path), lambda csv_row: mapping.update(
        {require_or_raise_map(csv_row, key_column): require_or_raise_map(csv_row, value_column)}
    ))

    return MappingProxyType(require_not_blank(mapping, f"Mapping file is empty: {path}"))
