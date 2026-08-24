from collections.abc import Callable
from typing import Any


class RepositoryDataExposer:
    def __init__(self, load_data: Callable[[str], Any], persist_data: Callable[[Any], None]) -> None:
        self._load_data = load_data
        self._persist_data = persist_data

    def expose(self, enriched_data_path) -> None:
        self._persist_data(self._load_data(enriched_data_path))

