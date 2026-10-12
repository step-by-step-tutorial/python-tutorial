from collections.abc import Mapping
from pathlib import Path

from test_data.config.settings import project_path
from test_data.util.csv_utils import read_csv_mapping, read_csv_rows
from test_data.util.file_utils import read_lines


class SourceRepository:
    """Reads the project's source files (text lists and CSV mappings) once and keeps them in memory."""

    def __init__(self) -> None:
        self.file_map: dict[Path, tuple[str, ...]] = {}
        self.csv_map: dict[tuple[Path, str, str], Mapping[str, str]] = {}
        self.csv_rows: dict[tuple[Path, str, str, int | None], tuple[dict[str, str], ...]] = {}

    def read_text_file(self, path: str) -> tuple[str, ...]:
        absolute_path = project_path(path)
        if absolute_path not in self.file_map:
            lines = read_lines(self._existing(absolute_path, "Source file"))
            if not lines:
                raise ValueError(f"Source file is empty: {absolute_path}")
            self.file_map[absolute_path] = lines

        return self.file_map[absolute_path]

    def read_csv_file(self, path: str, key_column: str, value_column: str) -> Mapping[str, str]:
        absolute_path = project_path(path)
        key = (absolute_path, key_column, value_column)
        if key not in self.csv_map:
            try:
                mapping = read_csv_mapping(self._existing(absolute_path, "CSV file"), key_column, value_column)
            except KeyError as error:
                raise KeyError(f"Column {error} not found in {absolute_path}.") from error
            if not mapping:
                raise ValueError(f"Mapping file is empty: {path}")
            self.csv_map[key] = mapping
        return self.csv_map[key]

    def read_csv_rows(
        self,
        path: str,
        key_column: str,
        key_value: str,
        limit: int | None = None,
    ) -> tuple[dict[str, str], ...]:
        """Return the rows whose key_column equals key_value, at most limit of them."""
        absolute_path = project_path(path)
        cache_key = (absolute_path, key_column, key_value, limit)
        if cache_key not in self.csv_rows:
            rows: list[dict[str, str]] = []
            for row in read_csv_rows(self._existing(absolute_path, "CSV file")):
                if row.get(key_column) != key_value:
                    continue
                rows.append(row)
                if limit is not None and len(rows) >= limit:
                    break
            self.csv_rows[cache_key] = tuple(rows)
        return self.csv_rows[cache_key]

    @staticmethod
    def _existing(path: Path, kind: str) -> Path:
        if not path.is_file():
            raise FileNotFoundError(f"{kind} not found: {path}")
        return path
