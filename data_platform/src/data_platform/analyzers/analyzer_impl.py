from typing import Any

from data_platform.analyzers.analyzer import Analyzer
from data_platform.analyzers.report import Report


class GroupAggregateAnalyzer(Analyzer):
    def __init__(
            self,
            name: str,
            group_by: str,
            value: str,
            aggregation: str,
            result_column: str | None = None,
    ) -> None:
        self.name = name
        self.group_by = group_by
        self.value = value
        self.aggregation = aggregation
        self.result_column = result_column or value

    def analyze(self, frame: Any) -> Report:
        result = (
            frame.groupby(self.group_by, as_index=False)[self.value]
            .agg(self.aggregation)
            .rename(columns={self.value: self.result_column})
            .reset_index(drop=True)
        )
        if self.aggregation == "sum":
            result = result.sort_values(self.result_column, ascending=False).reset_index(drop=True)
        return Report(self.name, result)


class RepositoryQueryAnalyzer(Analyzer):
    def __init__(self, repository: str, query: str) -> None:
        self.name = name
        self.query = query

    def analyze(self, frame: Any) -> Report:
        data = repository.find_by_queries([self.query])[self.query]
        return Report(self.name, data)
