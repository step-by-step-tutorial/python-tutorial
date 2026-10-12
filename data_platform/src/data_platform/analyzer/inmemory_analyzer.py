from typing import Any

from data_platform.analyzer.analyzer import Analyzer
from data_platform.model.aggregate_model import AggregateModel
from data_platform.model.report_model import ReportModel
from data_platform.repository.inmemory_database_repository import InmemoryDatabaseRepository


class GroupAggregateAnalyzer(Analyzer):
    def __init__(self, name: str, aggregate: AggregateModel) -> None:
        self.name = name
        self.aggregate = aggregate

    def analyze(self, source: Any) -> ReportModel:
        result = (
            source.groupby(self.aggregate.group_column, as_index=False)[self.aggregate.value_column]
            .agg(self.aggregate.aggregation_function)
            .rename(columns={self.aggregate.value_column: self.aggregate.output_column})
            .reset_index(drop=True)
        )
        return ReportModel(self.name, result)


class RepositoryQueryAnalyzer(Analyzer):
    def __init__(self, name: str, repository: InmemoryDatabaseRepository) -> None:
        self.name = name
        self._repository = repository

    def analyze(self, source: str) -> ReportModel:
        return ReportModel(self.name, self._repository.find_by_query(source))
