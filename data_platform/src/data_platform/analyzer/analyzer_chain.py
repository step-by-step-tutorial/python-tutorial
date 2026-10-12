from typing import Any

from data_platform.analyzer.analyzer import Analyzer
from data_platform.model.report_model import ReportModel


class AnalyzerChain:
    def __init__(self, analyzers: tuple[Analyzer, ...] = ()) -> None:
        self.analyzers = analyzers

    def analyze(self, dataframe: Any) -> tuple[ReportModel, ...]:
        return tuple(analyzer.analyze(dataframe) for analyzer in self.analyzers)
