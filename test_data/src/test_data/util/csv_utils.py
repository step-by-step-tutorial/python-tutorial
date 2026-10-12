from __future__ import annotations

import csv
from collections.abc import Callable, Iterable, Sequence
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from test_data.util.file_utils import absolute_project_path
from test_data.util.validation_utils import require_or_raise_map, require_not_blank


def write_csv(output_path: Path, headers: Sequence[str], rows: Iterable[Mapping[str, str]]) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(headers))
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def read_csv_file(path: str, consumer: Callable[[dict[str, str]], None]) -> None:
    """Pass every row of a project CSV file to consumer."""
    absolute_path = absolute_project_path(path)
    try:
        with absolute_path.open("r", encoding="utf-8", newline="") as file:
            for row in csv.DictReader(file):
                consumer(row)
    except FileNotFoundError as error:
        raise FileNotFoundError(f"CSV file not found: {absolute_path}") from error


def extract_map_from_csv(path: str, key_column: str, value_column: str) -> Mapping[str, str]:
    absolute_path = absolute_project_path(path)
    mapping: dict[str, str] = {}
    read_csv_file(str(absolute_path), lambda csv_row: mapping.update(
        {require_or_raise_map(csv_row, key_column): require_or_raise_map(csv_row, value_column)}
    ))

    return MappingProxyType(require_not_blank(mapping, f"Mapping file is empty: {path}"))
