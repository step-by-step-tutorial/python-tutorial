from typing import Mapping

from csv_utils import extract_map_from_csv
from file_utils import file_to_tuple


class SourceRepository:

    def __init__(self) -> None:
        self.file_map: dict[str, tuple[str, ...]] = {}
        self._mappings: dict[tuple[str, str, str], Mapping[str, str]] = {}

    def get_file_content(self, path: str) -> tuple[str, ...]:
        if path not in self.file_map:
            self.file_map[path] = file_to_tuple(path)

        return self.file_map[path]

    def mapping(self, path: str, key_column: str, value_column: str) -> Mapping[str, str]:
        key = (path, key_column, value_column)
        if key not in self._mappings:
            self._mappings[key] = extract_map_from_csv(path, key_column, value_column)
        return self._mappings[key]
