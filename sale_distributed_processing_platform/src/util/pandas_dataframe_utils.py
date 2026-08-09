from collections.abc import Iterable, Mapping, Sequence, Callable
from functools import reduce
from operator import and_

import pandas as pd
from pandas import DataFrame


def convert_numeric_column(df: DataFrame, column: str, default_value: float | int | None = None) -> DataFrame:
    if default_value is None:
        pd.to_numeric(df[column], errors="coerce")
    else:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(default_value)

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


def requires_column(df: pd.DataFrame, columns: set[str]) -> None:
    if df is None or columns is None:
        raise ValueError("required columns or dataframe is None")

    missing_columns = columns.difference(df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")


def rename_columns(df: DataFrame, columns: Mapping[str, str]) -> DataFrame:
    return df.rename(columns=columns)


def remove_duplicates(df: DataFrame, subset: str | Sequence[str] | None = None) -> DataFrame:
    return df.drop_duplicates(subset=subset)


def convert_boolean_column(df: DataFrame, column: str, default_value: bool = False) -> DataFrame:
    df[column] = (
        df[column]
        .map({
            True: True,
            False: False,
            "True": True,
            "False": False,
        })
        .fillna(default_value)
        .astype(bool)
    )

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
        decimal_places: int = 2
) -> DataFrame:
    df[alias_field] = (df[numerator_field] / df[denominator_field]).round(decimal_places)
    return df


def create_column(df: DataFrame, alias_field: str, function: Callable[[pd.Series], object]) -> DataFrame:
    df[alias_field] = df.apply(function, axis=1)
    return df


def average_by_group(
        df: DataFrame,
        group_field: str,
        original_field: str,
        alias_field: str
) -> DataFrame:
    return (
        df.groupby(group_field, as_index=False)[original_field]
        .mean()
        .rename(columns={original_field: alias_field})
    )
