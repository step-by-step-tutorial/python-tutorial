from collections.abc import Mapping

from pyspark.sql import DataFrame
from pyspark.sql import functions as sf

from dataset.sale.attribute import SALE_ATTRIBUTE as schema
from processor.base import DataProcessor
from transformation.spark.spark_ops import (
    convert_datetime_column,
    convert_numeric_column,
    fill_missing_by_column_average,
    fill_missing_by_group_average,
    remove_duplicates,
    sum_by_group,
    filter_dataframe,
)


class SparkSaleProcessor(DataProcessor[DataFrame]):
    def clean(self, dataframe: DataFrame) -> DataFrame:
        df = dataframe

        df = remove_duplicates(df, schema.order_id)
        df = convert_numeric_column(df, schema.quantity, default_value=1.0)
        df = convert_numeric_column(df, schema.unit_price)
        df = fill_missing_by_group_average(df, schema.category, schema.unit_price)
        df = fill_missing_by_column_average(df, schema.unit_price)
        df = convert_datetime_column(df, schema.order_date)

        return filter_dataframe(
            df=df,
            conditions=[
                sf.col(schema.order_date).isNotNull(),
                sf.col(schema.quantity) > 0,
                sf.col(schema.unit_price) >= 0,
            ]
        )

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        return (
            dataframe
            .withColumn(
                schema.total_price,
                sf.round(sf.col(schema.quantity) * sf.col(schema.unit_price), 2)
            )
            .withColumn(schema.year, sf.year(schema.order_date))
            .withColumn(schema.month, sf.month(schema.order_date))
        )

    def analyze(self, dataframe: DataFrame) -> Mapping[str, DataFrame]:
        return {
            "revenue_by_category": sum_by_group(
                df=dataframe,
                group_field=schema.category,
                original_field=schema.total_price,
                alias_field=schema.revenue
            ),
            "revenue_by_country": sum_by_group(
                df=dataframe,
                group_field=schema.country,
                original_field=schema.total_price,
                alias_field=schema.revenue
            )
        }
