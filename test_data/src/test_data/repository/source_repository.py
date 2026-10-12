from collections.abc import Callable, Hashable, Mapping
from pathlib import Path

from test_data.model.settings_model import SettingsModel
from test_data.util.csv_utils import read_csv_mapping, read_csv_rows
from test_data.util.file_utils import read_lines


class SourceRepository:
    """Reads the project's source files (text lists and CSV mappings) once per dataset run and keeps them in memory."""

    def __init__(self, settings: SettingsModel) -> None:
        self._settings = settings
        self._lines: dict[Path, tuple[str, ...]] = {}
        self._mappings: dict[tuple[Path, str, str], Mapping[str, str]] = {}
        self._rows: dict[tuple[Path, str, str, int | None], tuple[dict[str, str], ...]] = {}
        self._selected_rows: dict[Hashable, Mapping[str, str]] = {}

    def project_path(self, path: str | Path) -> Path:
        return self._settings.project_path(path)

    def read_text_file(self, path: str) -> tuple[str, ...]:
        absolute_path = self.project_path(path)
        if absolute_path not in self._lines:
            lines = read_lines(self._existing(absolute_path, "Source file"))
            if not lines:
                raise ValueError(f"Source file is empty: {absolute_path}")
            self._lines[absolute_path] = lines

        return self._lines[absolute_path]

    def read_csv_file(self, path: str, key_column: str, value_column: str) -> Mapping[str, str]:
        absolute_path = self.project_path(path)
        key = (absolute_path, key_column, value_column)
        if key not in self._mappings:
            try:
                mapping = read_csv_mapping(self._existing(absolute_path, "CSV file"), key_column, value_column)
            except KeyError as error:
                raise KeyError(f"Column {error} not found in {absolute_path}.") from error
            if not mapping:
                raise ValueError(f"Mapping file is empty: {path}")
            self._mappings[key] = mapping
        return self._mappings[key]

    def read_csv_rows(
        self,
        path: str,
        key_column: str,
        key_value: str,
        limit: int | None = None,
    ) -> tuple[dict[str, str], ...]:
        """Return the rows whose key_column equals key_value, at most limit of them."""
        absolute_path = self.project_path(path)
        cache_key = (absolute_path, key_column, key_value, limit)
        if cache_key not in self._rows:
            rows: list[dict[str, str]] = []
            for row in read_csv_rows(self._existing(absolute_path, "CSV file")):
                if row.get(key_column) != key_value:
                    continue
                rows.append(row)
                if limit is not None and len(rows) >= limit:
                    break
            self._rows[cache_key] = tuple(rows)
        return self._rows[cache_key]

    def select_row(self, key: Hashable, select: Callable[[], Mapping[str, str]]) -> Mapping[str, str]:
        """Return the row selected for key, selecting it on first use.

        Columns that read the same mapped CSV row (street, city and postcode of one address) share the selection,
        so a generated row stays consistent.
        """
        if key not in self._selected_rows:
            self._selected_rows[key] = select()
        return self._selected_rows[key]

    @staticmethod
    def _existing(path: Path, kind: str) -> Path:
        if not path.is_file():
            raise FileNotFoundError(f"{kind} not found: {path}")
        return path
