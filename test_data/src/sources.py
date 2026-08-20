import csv
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

class SourceRepository:

    def __init__(self, root: Path) -> None:
        self._root = Path(root)
        self._values: dict[str, tuple[str, ...]] = {}
        self._mappings: dict[tuple[str, str, str], Mapping[str, str]] = {}

    @property
    def root(self) -> Path:
        return self._root

    def resolve(self, relative_path: str) -> Path:
        return (self._root / relative_path).resolve()

    def values(self, relative_path: str) -> tuple[str, ...]:
        cached = self._values.get(relative_path)
        if cached is None:
            cached = self._values[relative_path] = self._read_values(relative_path)
        return cached

    def mapping(self, relative_path: str, key_column: str, value_column: str) -> Mapping[str, str]:
        cache_key = (relative_path, key_column, value_column)
        cached = self._mappings.get(cache_key)
        if cached is None:
            cached = self._mappings[cache_key] = self._read_mapping(
                relative_path, key_column, value_column
            )
        return cached

    def _read_values(self, relative_path: str) -> tuple[str, ...]:
        path = self.resolve(relative_path)
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError as error:
            raise Exception(f"Source file not found: {path}") from error

        values = tuple(line.strip() for line in text.splitlines() if line.strip())
        if not values:
            raise Exception(f"Source file is empty: {path}")
        return values

    def _read_mapping(
            self,
            relative_path: str,
            key_column: str,
            value_column: str,
    ) -> Mapping[str, str]:
        path = self.resolve(relative_path)
        try:
            with path.open("r", encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file)
                mapping = {
                    row[key_column]: row[value_column]
                    for row in self._checked_rows(reader, path, key_column, value_column)
                }
        except FileNotFoundError as error:
            raise Exception(f"Mapping file not found: {path}") from error

        if not mapping:
            raise Exception(f"Mapping file is empty: {path}")
        return MappingProxyType(mapping)

    @staticmethod
    def _checked_rows(
            reader: csv.DictReader,
            path: Path,
            key_column: str,
            value_column: str,
    ):
        for row in reader:
            if row.get(key_column) is None or row.get(value_column) is None:
                raise Exception(
                    f"Mapping file '{path}' must contain columns "
                    f"'{key_column}' and '{value_column}'."
                )
            yield row
