from collections.abc import Mapping

from pyspark.sql import DataFrame
from pyspark.sql import functions as sf

import dataset.house.model as schema
from processor.base import DataProcessor
from util.spark_dataframe_utils import (
    average_by_group,
    convert_boolean_column,
    convert_numeric_column,
    create_hash_column,
    divide_columns,
    filter_dataframe,
    remove_duplicates,
    rename_columns,
    trim_string_column,
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


class SparkHouseProcessor(DataProcessor[DataFrame]):

    def clean(self, dataframe: DataFrame) -> DataFrame:
        df = dataframe

        df = rename_columns(df, _RENAME)
        df = convert_numeric_column(df, schema.model.AREA)
        df = convert_numeric_column(df, schema.model.ROOM)
        df = convert_numeric_column(df, schema.model.PRICE)
        df = convert_numeric_column(df, schema.model.PRICE_USD)
        df = convert_boolean_column(df, schema.model.PARKING, default_value=False)
        df = convert_boolean_column(df, schema.model.WAREHOUSE, default_value=False)
        df = convert_boolean_column(df, schema.model.ELEVATOR, default_value=False)
        df = trim_string_column(df, schema.model.ADDRESS)
        df = remove_duplicates(df)

        return filter_dataframe(
            df=df,
            conditions=[
                sf.col(schema.model.AREA).isNotNull(),
                sf.col(schema.model.ROOM).isNotNull(),
                sf.col(schema.model.PRICE).isNotNull(),
                sf.col(schema.model.AREA) > 0,
                sf.col(schema.model.ROOM) >= 0,
                sf.col(schema.model.PRICE) > 0,
            ],
        )

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        df = dataframe

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

        return create_hash_column(
            df=df,
            alias_field=schema.model.LISTING_KEY,
            source_columns=[
                sf.format_string("%.6f", sf.col(schema.model.AREA)),
                sf.col(schema.model.ROOM).cast("long").cast("string"),
                sf.lower(sf.col(schema.model.PARKING).cast("string")),
                sf.lower(sf.col(schema.model.WAREHOUSE).cast("string")),
                sf.lower(sf.col(schema.model.ELEVATOR).cast("string")),
                sf.coalesce(sf.col(schema.model.ADDRESS), sf.lit("")),
                sf.format_string("%.6f", sf.col(schema.model.PRICE)),
                sf.when(
                    sf.col(schema.model.PRICE_USD).isNull(),
                    sf.lit(""),
                ).otherwise(
                    sf.format_string("%.6f", sf.col(schema.model.PRICE_USD))
                ),
            ],
        )

    def analyze(self, dataframe: DataFrame) -> Mapping[str, DataFrame]:
        return {
            "average_price_by_address": average_by_group(
                df=dataframe,
                group_field=schema.model.ADDRESS,
                original_field=schema.model.PRICE,
                alias_field="average_price",
            ),
            "average_price_per_square_meter_by_room": average_by_group(
                df=dataframe,
                group_field=schema.model.ROOM,
                original_field=schema.model.PRICE_PER_SQUARE_METER,
                alias_field="average_price_per_square_meter",
            ),
        }
