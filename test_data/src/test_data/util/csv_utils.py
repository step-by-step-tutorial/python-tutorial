import csv
from collections.abc import Iterable, Iterator, Mapping, Sequence
from pathlib import Path


def write_csv(output_path: Path, headers: Sequence[str], rows: Iterable[Mapping[str, str]]) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(headers))
        writer.writeheader()
        writer.writerows(rows)
    return path


def read_csv_rows(path: Path) -> Iterator[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        yield from csv.DictReader(file)


def read_csv_mapping(path: Path, key_column: str, value_column: str) -> dict[str, str]:
    """Map each row's key_column value to its value_column value; raise KeyError if a column is missing."""
    return {row[key_column]: row[value_column] for row in read_csv_rows(path)}
