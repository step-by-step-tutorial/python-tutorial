from collections.abc import Callable
from typing import Any


class DataWarehouseAnalyzer:
    def __init__(
        self,
        select_data: Callable[[list[str]], Any],
        query_names: list[str],
        present_results: Callable[[Any], None],
    ) -> None:
        self._select_data = select_data
        self._query_names = query_names
        self._present_results = present_results

    def analyze(self, enriched_data_path: str) -> None:
        self._present_results(self._select_data(self._query_names))
