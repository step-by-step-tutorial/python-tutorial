from typing import Any

from data_platform.analyzers.aggregate_model import AggregateSpecification
from data_platform.analyzers.analyzer import Analyzer
from data_platform.analyzers.report import Report
from data_platform.repository.database_repository import DatabaseRepository


class GroupAggregateAnalyzer(Analyzer):
    def __init__(self, name: str, specification: AggregateSpecification) -> None:
        self.name = name
        self.specification = specification

    def analyze(self, source: Any) -> Report:
        result = (
            source.groupby(self.specification.group_column, as_index=False)[self.specification.value_column]
            .agg(self.specification.aggregation_function)
            .rename(
                columns={
                    self.specification.value_column: self.specification.output_column,
                })
            .reset_index(drop=True)
        )
        return Report(self.name, result)


class RepositoryQueryAnalyzer(Analyzer):
    def __init__(self, name: str, repository: DatabaseRepository) -> None:
        self.name = name
        self._repository = repository

    def analyze(self, source: str) -> Report:
        result_set = self._repository.execute_query(source)
        return Report(self.name, result_set)
