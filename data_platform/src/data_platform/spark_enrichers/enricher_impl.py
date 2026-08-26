from typing import Any

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, concat_ws, date_format, dayofmonth, dayofweek, dayofyear, hour, month, quarter, round, sha2, year


class MultiplyColumnsEnricher:
    def __init__(self, left: str, right: str, target: str, decimals: int = 2) -> None:
        self.left, self.right, self.target, self.decimals = left, right, target, decimals

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        return dataframe.withColumn(self.target, round(col(self.left) * col(self.right), self.decimals))


class PercentageEnricher:
    def __init__(self, value: str, percent: str, target: str, decimals: int = 2) -> None:
        self.value, self.percent, self.target, self.decimals = value, percent, target, decimals

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        return dataframe.withColumn(self.target, round(col(self.value) * col(self.percent) / 100, self.decimals))


class CopyColumnEnricher:
    def __init__(self, source: str, target: str, decimals: int | None = None) -> None:
        self.source, self.target, self.decimals = source, target, decimals

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        value = col(self.source)
        return dataframe.withColumn(self.target, round(value, self.decimals) if self.decimals is not None else value)


class DivideColumnsEnricher:
    def __init__(self, numerator: str, denominator: str, target: str, decimals: int = 2) -> None:
        self.numerator, self.denominator, self.target, self.decimals = numerator, denominator, target, decimals

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        return dataframe.withColumn(self.target, round(col(self.numerator) / col(self.denominator), self.decimals))


class DatetimePartEnricher:
    def __init__(self, source: str, part: str, target: str) -> None:
        self.source, self.part, self.target = source, part, target

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        parts = {"year": year, "month": month, "day": dayofmonth, "dayofweek": dayofweek, "dayofyear": dayofyear, "hour": hour, "quarter": quarter}
        if self.part not in parts:
            raise ValueError(f"Unsupported datetime part: {self.part}")
        return dataframe.withColumn(self.target, parts[self.part](col(self.source)))


class HashColumnsEnricher:
    def __init__(self, columns: tuple[str, ...], target: str, separator: str = "|") -> None:
        self.columns, self.target, self.separator = columns, target, separator

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        return dataframe.withColumn(self.target, sha2(concat_ws(self.separator, *(col(column).cast("string") for column in self.columns)), 256))
