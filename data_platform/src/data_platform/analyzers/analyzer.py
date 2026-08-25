from typing import Any, Protocol

from data_platform.analyzers.report import Report


class Analyzer(Protocol):
    def analyze(self, frame: Any) -> Report:
        ...
