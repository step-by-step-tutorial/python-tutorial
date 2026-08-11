import pandas as pd
from pandas import DataFrame

from app_config import env_config as ec
from app_config.dataframe_schema import SALE_COLUMNS, DATA_REQUIRED_COLUMNS
from util.csv_utils import csv_to_dataframe
from util.file_utils import absolute_path
from util.pandas_dataframe_utils import (
    remove_duplicates,
    convert_numeric_column,
    fill_missing_by_group_average,
    fill_missing_by_column_average,
    convert_datetime_column,
    reset_index, sum_by_group,
    require_columns
)


def read_data(file_name: str) -> pd.DataFrame:
    df = csv_to_dataframe(absolute_path(ec.RESOURCES_DIR) / file_name)
    require_columns(df, DATA_REQUIRED_COLUMNS)
    return df


def clean_data(dataframe: DataFrame) -> DataFrame:
    df = dataframe.copy()

    df = remove_duplicates(df, SALE_COLUMNS.ORDER_ID)
    df = convert_numeric_column(df, SALE_COLUMNS.QUANTITY, default_value=1.0)
    df = convert_numeric_column(df, SALE_COLUMNS.UNIT_PRICE)
    df = fill_missing_by_group_average(df, SALE_COLUMNS.CATEGORY, SALE_COLUMNS.UNIT_PRICE)
    df = fill_missing_by_column_average(df, SALE_COLUMNS.UNIT_PRICE)
    df = convert_datetime_column(df, SALE_COLUMNS.ORDER_DATE)

    df = reset_index(
        df=df,
        conditions=[
            df[SALE_COLUMNS.ORDER_DATE].notna(),
            df[SALE_COLUMNS.QUANTITY] > 0,
            df[SALE_COLUMNS.UNIT_PRICE] >= 0,
        ]
    )

    return df


def enrich_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    df = dataframe.copy()
    df[SALE_COLUMNS.TOTAL_PRICE] = (df[SALE_COLUMNS.QUANTITY] * df[SALE_COLUMNS.UNIT_PRICE]).round(2)
    df[SALE_COLUMNS.YEAR] = df[SALE_COLUMNS.ORDER_DATE].dt.year
    df[SALE_COLUMNS.MONTH] = df[SALE_COLUMNS.ORDER_DATE].dt.month
    return df


def get_revenue_by_category(df: pd.DataFrame) -> pd.DataFrame:
    return sum_by_group(
        df=df,
        group_field=SALE_COLUMNS.CATEGORY,
        original_field=SALE_COLUMNS.TOTAL_PRICE,
        alias_field=SALE_COLUMNS.REVENUE
    )


def get_revenue_by_country(df: pd.DataFrame) -> pd.DataFrame:
    return sum_by_group(
        df=df,
        group_field=SALE_COLUMNS.COUNTRY,
        original_field=SALE_COLUMNS.TOTAL_PRICE,
        alias_field=SALE_COLUMNS.REVENUE
    )
