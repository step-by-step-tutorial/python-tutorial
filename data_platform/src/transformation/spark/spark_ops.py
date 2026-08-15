from collections.abc import Iterable, Mapping, Sequence

from pyspark.sql import Column, DataFrame, functions as sf


def remove_duplicates(df: DataFrame, *columns: str) -> DataFrame:
    return df.dropDuplicates(list(columns))


def convert_numeric_column(df: DataFrame, column: str, default_value: float | int | None = None) -> DataFrame:
    converted_column = sf.col(column).cast("double")
    if default_value is not None:
        converted_column = sf.coalesce(converted_column, sf.lit(default_value))
    return df.withColumn(column, converted_column)


def fill_missing_by_group_average(df: DataFrame, group_column: str, column: str) -> DataFrame:
    group_average_dataframe = df.groupBy(group_column).agg(sf.avg(column).alias("_group_average"))
    return (
        df.join(group_average_dataframe, on=group_column, how="left")
        .withColumn(column, sf.coalesce(sf.col(column), sf.col("_group_average")))
        .drop("_group_average")
    )


def fill_missing_by_column_average(df: DataFrame, column: str) -> DataFrame:
    average = df.select(sf.avg(column).alias("average")).first()["average"]
    if average is None:
        raise ValueError(f"No valid values are available for '{column}'.")
    return df.withColumn(column, sf.coalesce(sf.col(column), sf.lit(float(average))))


def convert_datetime_column(df: DataFrame, column: str) -> DataFrame:
    return df.withColumn(column, sf.try_to_timestamp(sf.col(column)))


def filter_dataframe(df: DataFrame, conditions: Iterable[Column]) -> DataFrame:
    from functools import reduce
    from operator import and_
    return df.filter(reduce(and_, conditions))


def sum_by_group(df: DataFrame, group_field: str, original_field: str, alias_field: str) -> DataFrame:
    return df.groupBy(group_field).agg(sf.sum(original_field).alias(alias_field)).orderBy(sf.col(alias_field).desc())


def rename_columns(df: DataFrame, columns: Mapping[str, str]) -> DataFrame:
    for original_field, alias_field in columns.items():
        df = df.withColumnRenamed(original_field, alias_field)
    return df


def convert_boolean_column(df: DataFrame, column: str, default_value: bool = False) -> DataFrame:
    return df.withColumn(
        column,
        sf.coalesce(sf.col(column).cast("boolean"), sf.lit(default_value)),
    )


def trim_string_column(df: DataFrame, column: str) -> DataFrame:
    return df.withColumn(column, sf.trim(sf.col(column)))


def divide_columns(
    df: DataFrame,
    numerator_field: str,
    denominator_field: str,
    alias_field: str,
    decimal_places: int = 2,
) -> DataFrame:
    return df.withColumn(alias_field, sf.round(sf.col(numerator_field) / sf.col(denominator_field), decimal_places))


def average_by_group(df: DataFrame, group_field: str, original_field: str, alias_field: str) -> DataFrame:
    return df.groupBy(group_field).agg(sf.avg(original_field).alias(alias_field))


def create_hash_column(
    df: DataFrame,
    alias_field: str,
    source_columns: Sequence[Column],
    separator: str = "|",
    bit_length: int = 256,
) -> DataFrame:
    return df.withColumn(alias_field, sf.sha2(sf.concat_ws(separator, *source_columns), bit_length))
