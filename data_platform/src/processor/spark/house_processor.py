from collections.abc import Mapping

from pyspark.sql import DataFrame
from pyspark.sql import functions as sf

from dataset.house.columns import house_columns as schema
from processor.base import DataProcessor
from transformation.spark.spark_ops import (
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
    schema.area_raw: schema.area,
    schema.room_raw: schema.room,
    schema.parking_raw: schema.parking,
    schema.warehouse_raw: schema.warehouse,
    schema.elevator_raw: schema.elevator,
    schema.address_raw: schema.address,
    schema.price_raw: schema.price,
    schema.price_usd_raw: schema.price_usd,
}


class SparkHouseProcessor(DataProcessor[DataFrame]):
    def clean(self, dataframe: DataFrame) -> DataFrame:
        df = dataframe

        df = rename_columns(df, _RENAME)
        df = convert_numeric_column(df, schema.area)
        df = convert_numeric_column(df, schema.room)
        df = convert_numeric_column(df, schema.price)
        df = convert_numeric_column(df, schema.price_usd)
        df = convert_boolean_column(df, schema.parking, default_value=False)
        df = convert_boolean_column(df, schema.warehouse, default_value=False)
        df = convert_boolean_column(df, schema.elevator, default_value=False)
        df = trim_string_column(df, schema.address)
        df = remove_duplicates(df)

        return filter_dataframe(
            df=df,
            conditions=[
                sf.col(schema.area).isNotNull(),
                sf.col(schema.room).isNotNull(),
                sf.col(schema.price).isNotNull(),
                sf.col(schema.area) > 0,
                sf.col(schema.room) >= 0,
                sf.col(schema.price) > 0,
            ],
        )

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        df = dataframe

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

        return create_hash_column(
            df=df,
            alias_field=schema.listing_key,
            source_columns=[
                sf.format_string("%.6f", sf.col(schema.area)),
                sf.col(schema.room).cast("long").cast("string"),
                sf.lower(sf.col(schema.parking).cast("string")),
                sf.lower(sf.col(schema.warehouse).cast("string")),
                sf.lower(sf.col(schema.elevator).cast("string")),
                sf.coalesce(sf.col(schema.address), sf.lit("")),
                sf.format_string("%.6f", sf.col(schema.price)),
                sf.when(
                    sf.col(schema.price_usd).isNull(),
                    sf.lit(""),
                ).otherwise(
                    sf.format_string("%.6f", sf.col(schema.price_usd))
                ),
            ],
        )

    def analyze(self, dataframe: DataFrame) -> Mapping[str, DataFrame]:
        return {
            "average_price_by_address": average_by_group(
                df=dataframe,
                group_field=schema.address,
                original_field=schema.price,
                alias_field="average_price",
            ),
            "average_price_per_square_meter_by_room": average_by_group(
                df=dataframe,
                group_field=schema.room,
                original_field=schema.price_per_square_meter,
                alias_field="average_price_per_square_meter",
            ),
        }
