from pyspark.sql import DataFrame

from data_platform.analyzers.aggregate_model import AggregateSpecification
from data_platform.analyzers.report import Report


class GroupAggregateAnalyzer:
    def __init__(self, name: str, specification: AggregateSpecification) -> None:
        self.name = name
        self.specification = specification

    def analyze(self, source: DataFrame) -> Report:
        result = source.groupBy(self.specification.group_column).agg({
            self.specification.value_column: self.specification.aggregation_function,
        })
        return Report(self.name, result.withColumnRenamed(
            f"{self.specification.aggregation_function}({self.specification.value_column})",
            self.specification.output_column,
        ))
