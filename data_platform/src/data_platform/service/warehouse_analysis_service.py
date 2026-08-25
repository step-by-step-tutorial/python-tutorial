from collections.abc import Callable
from typing import Any

from data_platform.model import DatasetAnalyzer


class WarehouseAnalyzer:
    def __init__(
            self,
            repository: Any,
            dataset_analyzer: DatasetAnalyzer,
            present_results: Callable[[Any], None],
    ) -> None:
        self._repository = repository
        self._dataset_analyzer = dataset_analyzer
        self._present_results = present_results

    def analyze(self, enriched_data_path=None) -> None:
        self._present_results(self._dataset_analyzer.analyze(self._repository))

