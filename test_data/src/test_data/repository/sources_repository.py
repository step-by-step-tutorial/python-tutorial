from typing import Mapping

from test_data.util.csv_utils import extract_map_from_csv, read_csv_file
from test_data.util.file_utils import absolute_project_path, file_to_tuple


class SourceRepository:

    def __init__(self) -> None:
        self.file_map: dict[str, tuple[str, ...]] = {}
        self.csv_map: dict[tuple[str, str, str], Mapping[str, str]] = {}
        self.csv_rows: dict[tuple[str, str, str], tuple[dict[str, str], ...]] = {}

    def read_text_file(self, path: str) -> tuple[str, ...]:
        path = str(absolute_project_path(path))
        if path not in self.file_map:
            self.file_map[path] = file_to_tuple(path)

        return self.file_map[path]

    def read_csv_file(self, path: str, key_column: str, value_column: str) -> Mapping[str, str]:
        path = str(absolute_project_path(path))
        key = (path, key_column, value_column)
        if key not in self.csv_map:
            self.csv_map[key] = extract_map_from_csv(path, key_column, value_column)
        return self.csv_map[key]

    def read_csv_rows(self, path: str, key_column: str, key_value: str) -> tuple[dict[str, str], ...]:
        path = str(absolute_project_path(path))
        cache_key = (path, key_column, key_value)
        if cache_key not in self.csv_rows:
            rows: list[dict[str, str]] = []
            read_csv_file(path, lambda row: rows.append(row) if row.get(key_column) == key_value else None)
            self.csv_rows[cache_key] = tuple(rows)
        return self.csv_rows[cache_key]
