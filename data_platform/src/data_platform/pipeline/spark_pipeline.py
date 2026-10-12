from functools import reduce
from typing import Any

from pyspark.sql import DataFrame

from data_platform.pipeline.pipeline import Pipeline


class SparkPipeline(Pipeline):

    def combine(self, dataframes: list[DataFrame]) -> DataFrame:
        return reduce(lambda left, right: left.unionByName(right, allowMissingColumns=True), dataframes)

    def count(self, dataframe: DataFrame) -> int:
        return dataframe.count()

    def is_empty(self, dataframe: DataFrame) -> bool:
        return dataframe.isEmpty()

    def to_dataframe(self, data: Any) -> DataFrame:
        return data
