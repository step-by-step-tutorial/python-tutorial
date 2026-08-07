from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as sf

from app_config import env_config as ec
from app_config.dataframe_schema import SALE_COLUMNS, DATA_REQUIRED_COLUMNS
from util.file_utils import build_absolute_path
from util.spark_dataframe_utils import (
    remove_duplicates,
    convert_numeric_column,
    fill_missing_by_group_average,
    fill_missing_by_column_average,
    convert_datetime_column,
    filter_dataframe,
    requires_column,
    sum_by_group,
)


def read_data(session: SparkSession, file_name, schema) -> DataFrame:
    if session is None:
        raise ValueError("Cannot read data because the Spark session is None.")
    if file_name is None:
        raise ValueError("Cannot read data because the input path is None.")
    if schema is None:
        raise ValueError("Cannot read data because the input schema is None.")

    df = (
        session.read
        .option("header", "true")
        .schema(schema)
        .csv(str(build_absolute_path(ec.RESOURCES_DIR) / file_name))
    )

    requires_column(df, DATA_REQUIRED_COLUMNS)
    return df


def clean_data(dataframe: DataFrame) -> DataFrame:
    df = dataframe

    df = remove_duplicates(df, SALE_COLUMNS.ORDER_ID)
    df = convert_numeric_column(df, SALE_COLUMNS.QUANTITY, default_value=1.0)
    df = convert_numeric_column(df, SALE_COLUMNS.UNIT_PRICE)
    df = fill_missing_by_group_average(df, SALE_COLUMNS.CATEGORY, SALE_COLUMNS.UNIT_PRICE)
    df = fill_missing_by_column_average(df, SALE_COLUMNS.UNIT_PRICE)
    df = convert_datetime_column(df, SALE_COLUMNS.ORDER_DATE)

    df = filter_dataframe(
        df=df,
        conditions=[
            sf.col(SALE_COLUMNS.ORDER_DATE).isNotNull(),
            sf.col(SALE_COLUMNS.QUANTITY) > 0,
            sf.col(SALE_COLUMNS.UNIT_PRICE) >= 0,
        ]
    )

    return df


def enrich_data(dataframe: DataFrame) -> DataFrame:
    return (
        dataframe
        .withColumn(
            SALE_COLUMNS.TOTAL_PRICE,
            sf.round(sf.col(SALE_COLUMNS.QUANTITY) * sf.col(SALE_COLUMNS.UNIT_PRICE), 2)
        )
        .withColumn(SALE_COLUMNS.YEAR, sf.year(SALE_COLUMNS.ORDER_DATE))
        .withColumn(SALE_COLUMNS.MONTH, sf.month(SALE_COLUMNS.ORDER_DATE))
    )


def get_revenue_by_category(df: DataFrame) -> DataFrame:
    return sum_by_group(
        df=df,
        group_field=SALE_COLUMNS.CATEGORY,
        original_field=SALE_COLUMNS.TOTAL_PRICE,
        alias_field=SALE_COLUMNS.REVENUE
    )


def get_revenue_by_country(df: DataFrame) -> DataFrame:
    return sum_by_group(
        df=df,
        group_field=SALE_COLUMNS.COUNTRY,
        original_field=SALE_COLUMNS.TOTAL_PRICE,
        alias_field=SALE_COLUMNS.REVENUE
    )
