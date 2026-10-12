from pyspark.sql import DataFrame
from pyspark.sql import functions as sf

from data_platform.analyzer.analyzer import Analyzer
from data_platform.model.aggregate_model import AggregateModel
from data_platform.model.report_model import ReportModel


class GroupAggregateAnalyzer(Analyzer):
    def __init__(self, name: str, aggregate: AggregateModel) -> None:
        self.name = name
        self.aggregate = aggregate

    def analyze(self, source: DataFrame) -> ReportModel:
        aggregation = getattr(sf, self.aggregate.aggregation_function)
        result = source.groupBy(self.aggregate.group_column).agg(
            aggregation(sf.col(self.aggregate.value_column)).alias(self.aggregate.output_column)
        )
        return ReportModel(self.name, result)
