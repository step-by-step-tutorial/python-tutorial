from collections.abc import Callable, Iterable, Mapping, Sequence
from functools import reduce
from operator import and_

import pandas as pd
from pandas import DataFrame


def convert_numeric_column(df: DataFrame, column: str, default_value: float | int | None = None) -> DataFrame:
    converted = pd.to_numeric(
        df[column].astype("string").str.replace(",", "", regex=False).str.strip(),
        errors="coerce",
    )
    if default_value is not None:
        converted = converted.fillna(default_value)
    df[column] = converted
    return df


def fill_missing_by_group_average(df: DataFrame, group_column: str, column: str) -> DataFrame:
    average = df.groupby(group_column)[column].transform("mean")
    df[column] = df[column].fillna(average)
    return df


def fill_missing_by_column_average(df: DataFrame, column: str) -> DataFrame:
    average = df[column].mean()
    if pd.isna(average):
        raise ValueError(f"No valid values are available for '{column}'.")
    df[column] = df[column].fillna(average)
    return df


def convert_datetime_column(df: DataFrame, column: str) -> DataFrame:
    df[column] = pd.to_datetime(df[column], errors="coerce")
    return df


def reset_index(df: DataFrame, conditions: Iterable[pd.Series]) -> DataFrame:
    return df.loc[reduce(and_, conditions)].reset_index(drop=True)


def sum_by_group(df: pd.DataFrame, group_field: str, original_field: str, alias_field: str) -> pd.DataFrame:
    return (
        df.groupby(group_field, as_index=False)[original_field]
        .sum()
        .rename(columns={original_field: alias_field})
        .sort_values(alias_field, ascending=False)
        .reset_index(drop=True)
    )


def rename_columns(df: DataFrame, columns: Mapping[str, str]) -> DataFrame:
    return df.rename(columns=columns)


def remove_duplicates(df: DataFrame, subset: str | Sequence[str] | None = None) -> DataFrame:
    return df.drop_duplicates(subset=subset)


def convert_boolean_column(df: DataFrame, column: str, default_value: bool = False) -> DataFrame:
    def _convert(value: object) -> bool:
        if pd.isna(value):
            return default_value

        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float)):
            return bool(value)

        normalized = str(value).strip().lower()
        if normalized == "":
            return default_value
        if normalized in {"true", "1", "yes", "y"}:
            return True
        if normalized in {"false", "0", "no", "n"}:
            return False
        return default_value

    df[column] = df[column].map(_convert).astype(bool)
    return df


def strip_string_column(df: DataFrame, column: str) -> DataFrame:
    df[column] = df[column].astype("string").str.strip()
    return df


def remove_rows_with_missing_values(df: DataFrame, columns: Sequence[str]) -> DataFrame:
    return df.dropna(subset=columns)


def divide_columns(
        df: DataFrame,
        numerator_field: str,
        denominator_field: str,
        alias_field: str,
        decimal_places: int = 2,
) -> DataFrame:
    df[alias_field] = (df[numerator_field] / df[denominator_field]).round(decimal_places)
    return df


def create_column(df: DataFrame, alias_field: str, function: Callable[[pd.Series], object]) -> DataFrame:
    df[alias_field] = df.apply(function, axis=1)
    return df


def average_by_group(df: DataFrame, group_field: str, original_field: str, alias_field: str) -> DataFrame:
    return (
        df.groupby(group_field, as_index=False)[original_field]
        .mean()
        .rename(columns={original_field: alias_field})
    )
