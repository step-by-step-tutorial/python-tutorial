import hashlib

import pandas as pd
from pandas import DataFrame

from data_platform.converter.pandas_converter import (
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
from data_platform.domain.house.attribute import HOUSE_ATTRIBUTE as schema
from data_platform.model import DatasetTransformer

_RENAME = {
    schema.area_raw: schema.area,
    schema.room_raw: schema.room,
    schema.parking_raw: schema.parking,
    schema.warehouse_raw: schema.warehouse,
    schema.elevator_raw: schema.elevator,
    schema.address_raw: schema.address,
    schema.price_raw: schema.price,
    schema.price_usd_raw: schema.price_usd,
}


def create_listing_key(row: pd.Series) -> str:
    price_usd = (
        ""
        if pd.isna(row[schema.price_usd])
        else f"{float(row[schema.price_usd]):.6f}"
    )

    parts = (
        f"{float(row[schema.area]):.6f}",
        str(int(row[schema.room])),
        str(bool(row[schema.parking])).lower(),
        str(bool(row[schema.warehouse])).lower(),
        str(bool(row[schema.elevator])).lower(),
        "" if pd.isna(row[schema.address]) else str(row[schema.address]),
        f"{float(row[schema.price]):.6f}",
        price_usd,
    )

    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


class InmemoryHouseTransformer(DatasetTransformer[DataFrame]):

    def clean(self, dataframe: DataFrame) -> DataFrame:
        df = dataframe.copy()

        df = rename_columns(df, _RENAME)

        df = convert_numeric_column(df, schema.area)
        df = convert_numeric_column(df, schema.room)
        df = convert_numeric_column(df, schema.price)
        df = convert_numeric_column(df, schema.price_usd)

        df = convert_boolean_column(df, schema.parking)
        df = convert_boolean_column(df, schema.warehouse)
        df = convert_boolean_column(df, schema.elevator)

        df = strip_string_column(df, schema.address)

        df = remove_rows_with_missing_values(
            df,
            [
                schema.area,
                schema.room,
                schema.price,
            ],
        )

        df = reset_index(
            df=df,
            conditions=[
                df[schema.area] > 0,
                df[schema.room] >= 0,
                df[schema.price] > 0,
            ],
        )

        df = remove_duplicates(df)

        return df

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        df = dataframe.copy()

        df = divide_columns(
            df=df,
            numerator_field=schema.price,
            denominator_field=schema.area,
            alias_field=schema.price_per_square_meter,
        )

        df = divide_columns(
            df=df,
            numerator_field=schema.price_usd,
            denominator_field=schema.area,
            alias_field=schema.price_usd_per_square_meter,
        )

        df = create_column(
            df=df,
            alias_field=schema.listing_key,
            function=create_listing_key,
        )

        return df
