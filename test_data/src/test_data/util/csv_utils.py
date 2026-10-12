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


def filter_rows(rows: Iterable[Mapping[str, str]], column: str, values: Iterable[str]) -> tuple[Mapping[str, str], ...]:
    """Keep the rows whose column holds one of values."""
    allowed = set(values)
    return tuple(row for row in rows if row.get(column) in allowed)


def rows_with_values(rows: Iterable[Mapping[str, str]], columns: Iterable[str]) -> tuple[Mapping[str, str], ...]:
    """Keep the rows that have a non-empty value in every one of columns."""
    required = tuple(columns)
    return tuple(row for row in rows if all(row.get(column) for column in required))
