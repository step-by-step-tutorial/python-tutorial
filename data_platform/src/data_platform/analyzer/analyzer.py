from typing import Any, Protocol

from data_platform.model.report_model import ReportModel


class Analyzer(Protocol):
    def analyze(self, source: Any) -> ReportModel:
        ...
