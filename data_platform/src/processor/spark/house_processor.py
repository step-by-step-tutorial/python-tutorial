from collections.abc import Mapping

from pyspark.sql import DataFrame
from pyspark.sql import functions as sf

from dataset.house import model as schema
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
    schema.model.area_raw: schema.model.area,
    schema.model.room_raw: schema.model.room,
    schema.model.parking_raw: schema.model.parking,
    schema.model.warehouse_raw: schema.model.warehouse,
    schema.model.elevator_raw: schema.model.elevator,
    schema.model.address_raw: schema.model.address,
    schema.model.price_raw: schema.model.price,
    schema.model.price_usd_raw: schema.model.price_usd,
}


class SparkHouseProcessor(DataProcessor[DataFrame]):
    def clean(self, dataframe: DataFrame) -> DataFrame:
        df = dataframe

        df = rename_columns(df, _RENAME)
        df = convert_numeric_column(df, schema.model.area)
        df = convert_numeric_column(df, schema.model.room)
        df = convert_numeric_column(df, schema.model.price)
        df = convert_numeric_column(df, schema.model.price_usd)
        df = convert_boolean_column(df, schema.model.parking, default_value=False)
        df = convert_boolean_column(df, schema.model.warehouse, default_value=False)
        df = convert_boolean_column(df, schema.model.elevator, default_value=False)
        df = trim_string_column(df, schema.model.address)
        df = remove_duplicates(df)

        return filter_dataframe(
            df=df,
            conditions=[
                sf.col(schema.model.area).isNotNull(),
                sf.col(schema.model.room).isNotNull(),
                sf.col(schema.model.price).isNotNull(),
                sf.col(schema.model.area) > 0,
                sf.col(schema.model.room) >= 0,
                sf.col(schema.model.price) > 0,
            ],
        )

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        df = dataframe

        df = divide_columns(
            df=df,
            numerator_field=schema.model.price,
            denominator_field=schema.model.area,
            alias_field=schema.model.price_per_square_meter,
        )

        df = divide_columns(
            df=df,
            numerator_field=schema.model.price_usd,
            denominator_field=schema.model.area,
            alias_field=schema.model.price_usd_per_square_meter,
        )

        return create_hash_column(
            df=df,
            alias_field=schema.model.listing_key,
            source_columns=[
                sf.format_string("%.6f", sf.col(schema.model.area)),
                sf.col(schema.model.room).cast("long").cast("string"),
                sf.lower(sf.col(schema.model.parking).cast("string")),
                sf.lower(sf.col(schema.model.warehouse).cast("string")),
                sf.lower(sf.col(schema.model.elevator).cast("string")),
                sf.coalesce(sf.col(schema.model.address), sf.lit("")),
                sf.format_string("%.6f", sf.col(schema.model.price)),
                sf.when(
                    sf.col(schema.model.price_usd).isNull(),
                    sf.lit(""),
                ).otherwise(
                    sf.format_string("%.6f", sf.col(schema.model.price_usd))
                ),
            ],
        )

    def analyze(self, dataframe: DataFrame) -> Mapping[str, DataFrame]:
        return {
            "average_price_by_address": average_by_group(
                df=dataframe,
                group_field=schema.model.address,
                original_field=schema.model.price,
                alias_field="average_price",
            ),
            "average_price_per_square_meter_by_room": average_by_group(
                df=dataframe,
                group_field=schema.model.room,
                original_field=schema.model.price_per_square_meter,
                alias_field="average_price_per_square_meter",
            ),
        }

