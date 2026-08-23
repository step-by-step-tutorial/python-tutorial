from collections.abc import Callable
from typing import Any


class RepositoryDataPopulator:
    def __init__(self, load_data: Callable[[str], Any], persist_data: Callable[[Any], None]) -> None:
        self._load_data = load_data
        self._persist_data = persist_data

    def populate(self, enriched_data_path: str) -> None:
        self._persist_data(self._load_data(enriched_data_path))
