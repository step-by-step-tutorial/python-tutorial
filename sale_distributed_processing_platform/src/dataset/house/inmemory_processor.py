import hashlib
from collections.abc import Mapping

import pandas as pd
from pandas import DataFrame

import schema
from dataset.definition import DataProcessor
from util.pandas_dataframe_utils import (
    average_by_group,
    convert_boolean_column,
    convert_numeric_column,
    create_column,
    divide_columns,
    remove_duplicates,
    remove_rows_with_missing_values,
    rename_columns,
    reset_index,
    strip_string_column,
)

_RENAME = {
    schema.dataset_model_instance.AREA_RAW: schema.dataset_model_instance.AREA,
    schema.dataset_model_instance.ROOM_RAW: schema.dataset_model_instance.ROOM,
    schema.dataset_model_instance.PARKING_RAW: schema.dataset_model_instance.PARKING,
    schema.dataset_model_instance.WAREHOUSE_RAW: schema.dataset_model_instance.WAREHOUSE,
    schema.dataset_model_instance.ELEVATOR_RAW: schema.dataset_model_instance.ELEVATOR,
    schema.dataset_model_instance.ADDRESS_RAW: schema.dataset_model_instance.ADDRESS,
    schema.dataset_model_instance.PRICE_RAW: schema.dataset_model_instance.PRICE,
    schema.dataset_model_instance.PRICE_USD_RAW: schema.dataset_model_instance.PRICE_USD,
}


def create_listing_key(row: pd.Series) -> str:
    price_usd = (
        ""
        if pd.isna(row[schema.dataset_model_instance.PRICE_USD])
        else f"{float(row[schema.dataset_model_instance.PRICE_USD]):.6f}"
    )

    parts = (
        f"{float(row[schema.dataset_model_instance.AREA]):.6f}",
        str(int(row[schema.dataset_model_instance.ROOM])),
        str(bool(row[schema.dataset_model_instance.PARKING])).lower(),
        str(bool(row[schema.dataset_model_instance.WAREHOUSE])).lower(),
        str(bool(row[schema.dataset_model_instance.ELEVATOR])).lower(),
        "" if pd.isna(row[schema.dataset_model_instance.ADDRESS]) else str(row[schema.dataset_model_instance.ADDRESS]),
        f"{float(row[schema.dataset_model_instance.PRICE]):.6f}",
        price_usd,
    )

    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


class InmemoryHouseProcessor(DataProcessor[DataFrame]):

    def clean(self, dataframe: DataFrame) -> DataFrame:
        df = dataframe.copy()

        df = rename_columns(df, _RENAME)

        df = convert_numeric_column(df, schema.dataset_model_instance.AREA)
        df = convert_numeric_column(df, schema.dataset_model_instance.ROOM)
        df = convert_numeric_column(df, schema.dataset_model_instance.PRICE)
        df = convert_numeric_column(df, schema.dataset_model_instance.PRICE_USD)

        df = convert_boolean_column(df, schema.dataset_model_instance.PARKING)
        df = convert_boolean_column(df, schema.dataset_model_instance.WAREHOUSE)
        df = convert_boolean_column(df, schema.dataset_model_instance.ELEVATOR)

        df = strip_string_column(df, schema.dataset_model_instance.ADDRESS)

        df = remove_rows_with_missing_values(
            df,
            [
                schema.dataset_model_instance.AREA,
                schema.dataset_model_instance.ROOM,
                schema.dataset_model_instance.PRICE,
            ],
        )

        df = reset_index(
            df=df,
            conditions=[
                df[schema.dataset_model_instance.AREA] > 0,
                df[schema.dataset_model_instance.ROOM] >= 0,
                df[schema.dataset_model_instance.PRICE] > 0,
                ],
        )

        df = remove_duplicates(df)

        return df

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        df = dataframe.copy()

        df = divide_columns(
            df=df,
            numerator_field=schema.dataset_model_instance.PRICE,
            denominator_field=schema.dataset_model_instance.AREA,
            alias_field=schema.dataset_model_instance.PRICE_PER_SQUARE_METER,
        )

        df = divide_columns(
            df=df,
            numerator_field=schema.dataset_model_instance.PRICE_USD,
            denominator_field=schema.dataset_model_instance.AREA,
            alias_field=schema.dataset_model_instance.PRICE_USD_PER_SQUARE_METER,
        )

        df = create_column(
            df=df,
            alias_field=schema.dataset_model_instance.LISTING_KEY,
            function=create_listing_key,
        )

        return df

    def analyze(self, dataframe: DataFrame) -> Mapping[str, DataFrame]:
        return {
            "average_price_by_address": average_by_group(
                df=dataframe,
                group_field=schema.dataset_model_instance.ADDRESS,
                original_field=schema.dataset_model_instance.PRICE,
                alias_field="average_price",
            ),
            "average_price_by_square_meter": average_by_group(
                df=dataframe,
                group_field=schema.dataset_model_instance.ROOM,
                original_field=schema.dataset_model_instance.PRICE_PER_SQUARE_METER,
                alias_field="average_price_by_square_meter",
            ),
        }