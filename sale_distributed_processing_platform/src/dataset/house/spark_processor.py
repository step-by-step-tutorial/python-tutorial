from collections.abc import Mapping

from pyspark.sql import DataFrame
from pyspark.sql import functions as sf

import dataset.house.schema as schema
from dataset.definition import DataProcessor
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
    schema.dataset_model_instance.AREA_RAW: schema.dataset_model_instance.AREA,
    schema.dataset_model_instance.ROOM_RAW: schema.dataset_model_instance.ROOM,
    schema.dataset_model_instance.PARKING_RAW: schema.dataset_model_instance.PARKING,
    schema.dataset_model_instance.WAREHOUSE_RAW: schema.dataset_model_instance.WAREHOUSE,
    schema.dataset_model_instance.ELEVATOR_RAW: schema.dataset_model_instance.ELEVATOR,
    schema.dataset_model_instance.ADDRESS_RAW: schema.dataset_model_instance.ADDRESS,
    schema.dataset_model_instance.PRICE_RAW: schema.dataset_model_instance.PRICE,
    schema.dataset_model_instance.PRICE_USD_RAW: schema.dataset_model_instance.PRICE_USD,
}


class SparkHouseProcessor(DataProcessor[DataFrame]):

    def clean(self, dataframe: DataFrame) -> DataFrame:
        df = dataframe

        df = rename_columns(df, _RENAME)
        df = convert_numeric_column(df, schema.dataset_model_instance.AREA)
        df = convert_numeric_column(df, schema.dataset_model_instance.ROOM)
        df = convert_numeric_column(df, schema.dataset_model_instance.PRICE)
        df = convert_numeric_column(df, schema.dataset_model_instance.PRICE_USD)
        df = convert_boolean_column(df, schema.dataset_model_instance.PARKING, default_value=False)
        df = convert_boolean_column(df, schema.dataset_model_instance.WAREHOUSE, default_value=False)
        df = convert_boolean_column(df, schema.dataset_model_instance.ELEVATOR, default_value=False)
        df = trim_string_column(df, schema.dataset_model_instance.ADDRESS)
        df = remove_duplicates(df)

        return filter_dataframe(
            df=df,
            conditions=[
                sf.col(schema.dataset_model_instance.AREA).isNotNull(),
                sf.col(schema.dataset_model_instance.ROOM).isNotNull(),
                sf.col(schema.dataset_model_instance.PRICE).isNotNull(),
                sf.col(schema.dataset_model_instance.AREA) > 0,
                sf.col(schema.dataset_model_instance.ROOM) >= 0,
                sf.col(schema.dataset_model_instance.PRICE) > 0,
            ],
        )

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        df = dataframe

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

        return create_hash_column(
            df=df,
            alias_field=schema.dataset_model_instance.LISTING_KEY,
            source_columns=[
                sf.format_string("%.6f", sf.col(schema.dataset_model_instance.AREA)),
                sf.col(schema.dataset_model_instance.ROOM).cast("long").cast("string"),
                sf.lower(sf.col(schema.dataset_model_instance.PARKING).cast("string")),
                sf.lower(sf.col(schema.dataset_model_instance.WAREHOUSE).cast("string")),
                sf.lower(sf.col(schema.dataset_model_instance.ELEVATOR).cast("string")),
                sf.coalesce(sf.col(schema.dataset_model_instance.ADDRESS), sf.lit("")),
                sf.format_string("%.6f", sf.col(schema.dataset_model_instance.PRICE)),
                sf.when(
                    sf.col(schema.dataset_model_instance.PRICE_USD).isNull(),
                    sf.lit(""),
                ).otherwise(
                    sf.format_string("%.6f", sf.col(schema.dataset_model_instance.PRICE_USD))
                ),
            ],
        )

    def analyze(self, dataframe: DataFrame) -> Mapping[str, DataFrame]:
        return {
            "average_price_by_address": average_by_group(
                df=dataframe,
                group_field=schema.dataset_model_instance.ADDRESS,
                original_field=schema.dataset_model_instance.PRICE,
                alias_field="average_price",
            ),
            "average_price_per_square_meter_by_room": average_by_group(
                df=dataframe,
                group_field=schema.dataset_model_instance.ROOM,
                original_field=schema.dataset_model_instance.PRICE_PER_SQUARE_METER,
                alias_field="average_price_per_square_meter",
            ),
        }
