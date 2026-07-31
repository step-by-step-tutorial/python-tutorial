from collections.abc import Iterable
from functools import reduce
from operator import and_

import pandas as pd
from pandas import DataFrame


def remove_duplicates(df: DataFrame, *columns: str) -> DataFrame:
    return df.drop_duplicates(subset=columns, keep="first")


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
