import hashlib
from collections.abc import Mapping

import pandas as pd
from pandas import DataFrame
import dataset.house.model as schema
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
    schema.model.AREA_RAW: schema.model.AREA,
    schema.model.ROOM_RAW: schema.model.ROOM,
    schema.model.PARKING_RAW: schema.model.PARKING,
    schema.model.WAREHOUSE_RAW: schema.model.WAREHOUSE,
    schema.model.ELEVATOR_RAW: schema.model.ELEVATOR,
    schema.model.ADDRESS_RAW: schema.model.ADDRESS,
    schema.model.PRICE_RAW: schema.model.PRICE,
    schema.model.PRICE_USD_RAW: schema.model.PRICE_USD,
}


def create_listing_key(row: pd.Series) -> str:
    price_usd = (
        ""
        if pd.isna(row[schema.model.PRICE_USD])
        else f"{float(row[schema.model.PRICE_USD]):.6f}"
    )

    parts = (
        f"{float(row[schema.model.AREA]):.6f}",
        str(int(row[schema.model.ROOM])),
        str(bool(row[schema.model.PARKING])).lower(),
        str(bool(row[schema.model.WAREHOUSE])).lower(),
        str(bool(row[schema.model.ELEVATOR])).lower(),
        "" if pd.isna(row[schema.model.ADDRESS]) else str(row[schema.model.ADDRESS]),
        f"{float(row[schema.model.PRICE]):.6f}",
        price_usd,
    )

    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


class InmemoryHouseProcessor(DataProcessor[DataFrame]):

    def clean(self, dataframe: DataFrame) -> DataFrame:
        df = dataframe.copy()

        df = rename_columns(df, _RENAME)

        df = convert_numeric_column(df, schema.model.AREA)
        df = convert_numeric_column(df, schema.model.ROOM)
        df = convert_numeric_column(df, schema.model.PRICE)
        df = convert_numeric_column(df, schema.model.PRICE_USD)

        df = convert_boolean_column(df, schema.model.PARKING)
        df = convert_boolean_column(df, schema.model.WAREHOUSE)
        df = convert_boolean_column(df, schema.model.ELEVATOR)

        df = strip_string_column(df, schema.model.ADDRESS)

        df = remove_rows_with_missing_values(
            df,
            [
                schema.model.AREA,
                schema.model.ROOM,
                schema.model.PRICE,
            ],
        )

        df = reset_index(
            df=df,
            conditions=[
                df[schema.model.AREA] > 0,
                df[schema.model.ROOM] >= 0,
                df[schema.model.PRICE] > 0,
                ],
        )

        df = remove_duplicates(df)

        return df

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        df = dataframe.copy()

        df = divide_columns(
            df=df,
            numerator_field=schema.model.PRICE,
            denominator_field=schema.model.AREA,
            alias_field=schema.model.PRICE_PER_SQUARE_METER,
        )

        df = divide_columns(
            df=df,
            numerator_field=schema.model.PRICE_USD,
            denominator_field=schema.model.AREA,
            alias_field=schema.model.PRICE_USD_PER_SQUARE_METER,
        )

        df = create_column(
            df=df,
            alias_field=schema.model.LISTING_KEY,
            function=create_listing_key,
        )

        return df

    def analyze(self, dataframe: DataFrame) -> Mapping[str, DataFrame]:
        return {
            "average_price_by_address": average_by_group(
                df=dataframe,
                group_field=schema.model.ADDRESS,
                original_field=schema.model.PRICE,
                alias_field="average_price",
            ),
            "average_price_by_square_meter": average_by_group(
                df=dataframe,
                group_field=schema.model.ROOM,
                original_field=schema.model.PRICE_PER_SQUARE_METER,
                alias_field="average_price_by_square_meter",
            ),
        }