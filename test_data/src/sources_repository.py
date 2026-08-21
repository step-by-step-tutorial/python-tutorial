from typing import Mapping

from csv_utils import extract_map_from_csv
from file_utils import file_to_tuple


class SourceRepository:

    def __init__(self) -> None:
        self.file_map: dict[str, tuple[str, ...]] = {}
        self.csv_map: dict[tuple[str, str, str], Mapping[str, str]] = {}

    def read_text_file(self, path: str) -> tuple[str, ...]:
        if path not in self.file_map:
            self.file_map[path] = file_to_tuple(path)

        return self.file_map[path]

    def read_csv_file(self, path: str, key_column: str, value_column: str) -> Mapping[str, str]:
        key = (path, key_column, value_column)
        if key not in self.csv_map:
            self.csv_map[key] = extract_map_from_csv(path, key_column, value_column)
        return self.csv_map[key]
