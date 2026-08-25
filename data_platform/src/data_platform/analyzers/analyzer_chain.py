from typing import Any

from data_platform.analyzers.analyzer import Analyzer
from data_platform.analyzers.report import Report


class AnalyzerChain:
    def __init__(self, analyzers: tuple[Analyzer, ...] = ()) -> None:
        self.analyzers = analyzers

    def analyze(self, frame: Any) -> tuple[Report, ...]:
        return tuple(analyzer.analyze(frame) for analyzer in self.analyzers)
