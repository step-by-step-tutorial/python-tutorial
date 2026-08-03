from collections.abc import Iterable
from functools import reduce
from operator import and_

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as sf


def remove_duplicates(df: DataFrame, *columns: str) -> DataFrame:
    return df.dropDuplicates(list(columns))


def convert_numeric_column(df: DataFrame, column: str, default_value: float | int | None = None) -> DataFrame:
    converted_column = sf.col(column).cast("double")

    if default_value is not None:
        converted_column = sf.coalesce(converted_column, sf.lit(default_value))

    return df.withColumn(column, converted_column)


def fill_missing_by_group_average(df: DataFrame, group_column: str, column: str) -> DataFrame:
    group_average_dataframe = (
        df
        .groupBy(group_column)
        .agg(sf.avg(column).alias("_group_average"))
    )

    average = (
        df
        .join(group_average_dataframe, on=group_column, how="left")
        .withColumn(column, sf.coalesce(sf.col(column), sf.col("_group_average")))
        .drop("_group_average")
    )
    return average


def fill_missing_by_column_average(df: DataFrame, column: str) -> DataFrame:
    average = df.select(sf.avg(column).alias("average")).first()["average"]

    if average is None:
        raise ValueError(f"No valid values are available for '{column}'.")

    return df.withColumn(column, sf.coalesce(sf.col(column), sf.lit(float(average))))


def convert_datetime_column(df: DataFrame, column: str) -> DataFrame:
    return df.withColumn(column, sf.try_to_timestamp(sf.col(column)))


def filter_dataframe(df: DataFrame, conditions: Iterable[Column]) -> DataFrame:
    return df.filter(reduce(and_, conditions))


def sum_by_group(df: DataFrame, group_field: str, original_field: str, alias_field: str) -> DataFrame:
    return (
        df
        .groupBy(group_field)
        .agg(sf.sum(original_field).alias(alias_field))
        .orderBy(sf.col(alias_field).desc())
    )


def requires_column(df: DataFrame, columns: set[str]) -> None:
    if df is None or columns is None:
        raise ValueError("required columns or dataframe is None")

    missing_columns = columns.difference(df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")
