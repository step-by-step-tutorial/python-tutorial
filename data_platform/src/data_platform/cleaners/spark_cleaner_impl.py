from collections.abc import Mapping, Sequence
from typing import Any

from pyspark.sql import DataFrame, Window
from pyspark.sql.functions import avg, coalesce, col, lit, lower, regexp_replace, to_timestamp, trim, when


class DropDuplicatesCleaner:
    def __init__(self, subset: str | Sequence[str] | None = None) -> None:
        self.subset = subset

    def clean(self, dataframe: DataFrame) -> DataFrame:
        return dataframe.dropDuplicates(self.subset)


class NumericColumnCleaner:
    def __init__(self, column: str, default_value: float | int | None = None) -> None:
        self.column, self.default_value = column, default_value

    def clean(self, dataframe: DataFrame) -> DataFrame:
        value = regexp_replace(trim(col(self.column).cast("string")), ",", "").cast("double")
        if self.default_value is not None:
            value = coalesce(value, lit(self.default_value))
        return dataframe.withColumn(self.column, value)


class CastColumnCleaner:
    def __init__(self, column: str, dtype: str) -> None:
        self.column, self.dtype = column, dtype

    def clean(self, dataframe: DataFrame) -> DataFrame:
        return dataframe.withColumn(self.column, col(self.column).cast(self.dtype))


class ToDatetimeCleaner:
    def __init__(self, column: str) -> None:
        self.column = column

    def clean(self, dataframe: DataFrame) -> DataFrame:
        return dataframe.withColumn(self.column, to_timestamp(self.column))


class BooleanColumnCleaner:
    def __init__(self, column: str, default_value: bool = False) -> None:
        self.column, self.default_value = column, default_value

    def clean(self, dataframe: DataFrame) -> DataFrame:
        value = when(lower(trim(col(self.column).cast("string"))).isin("true", "1", "yes", "y"), lit(True)).otherwise(lit(False))
        return dataframe.withColumn(self.column, coalesce(value, lit(self.default_value)))


class RenameColumnsCleaner:
    def __init__(self, columns: Mapping[str, str]) -> None:
        self.columns = columns

    def clean(self, dataframe: DataFrame) -> DataFrame:
        for source, target in self.columns.items():
            dataframe = dataframe.withColumnRenamed(source, target)
        return dataframe


class StripColumnCleaner:
    def __init__(self, column: str) -> None:
        self.column = column

    def clean(self, dataframe: DataFrame) -> DataFrame:
        return dataframe.withColumn(self.column, trim(col(self.column).cast("string")))


class FillMissingByGroupAverageCleaner:
    def __init__(self, group_column: str, column: str) -> None:
        self.group_column, self.column = group_column, column

    def clean(self, dataframe: DataFrame) -> DataFrame:
        window = Window.partitionBy(self.group_column)
        return dataframe.withColumn(self.column, coalesce(col(self.column), avg(self.column).over(window)))


class FillMissingByColumnAverageCleaner:
    def __init__(self, column: str) -> None:
        self.column = column

    def clean(self, dataframe: DataFrame) -> DataFrame:
        window = Window.rowsBetween(Window.unboundedPreceding, Window.unboundedFollowing)
        return dataframe.withColumn(self.column, coalesce(col(self.column), avg(self.column).over(window)))
