from collections.abc import Callable
from typing import Any

from data_platform.model import DatasetAnalyzer


class DataFrameAnalyzer:
    def __init__(
            self,
            load_data: Callable[[str], Any],
            dataset_analyzer: DatasetAnalyzer,
            present_results: Callable[[Any], None],
    ) -> None:
        self._load_data = load_data
        self._dataset_analyzer = dataset_analyzer
        self._present_results = present_results

    def analyze(self, enriched_data_path) -> None:
        self._present_results(self._dataset_analyzer.analyze(self._load_data(enriched_data_path)))

