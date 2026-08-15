from collections.abc import Mapping

from pyspark.sql import DataFrame
from pyspark.sql import functions as sf

from dataset.sale import model as schema
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

        df = remove_duplicates(df, schema.model.order_id)
        df = convert_numeric_column(df, schema.model.quantity, default_value=1.0)
        df = convert_numeric_column(df, schema.model.unit_price)
        df = fill_missing_by_group_average(df, schema.model.category, schema.model.unit_price)
        df = fill_missing_by_column_average(df, schema.model.unit_price)
        df = convert_datetime_column(df, schema.model.order_date)

        return filter_dataframe(
            df=df,
            conditions=[
                sf.col(schema.model.order_date).isNotNull(),
                sf.col(schema.model.quantity) > 0,
                sf.col(schema.model.unit_price) >= 0,
            ]
        )

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        return (
            dataframe
            .withColumn(
                schema.model.total_price,
                sf.round(sf.col(schema.model.quantity) * sf.col(schema.model.unit_price), 2)
            )
            .withColumn(schema.model.year, sf.year(schema.model.order_date))
            .withColumn(schema.model.month, sf.month(schema.model.order_date))
        )

    def analyze(self, dataframe: DataFrame) -> Mapping[str, DataFrame]:
        return {
            "revenue_by_category": sum_by_group(
                df=dataframe,
                group_field=schema.model.category,
                original_field=schema.model.total_price,
                alias_field=schema.model.revenue
            ),
            "revenue_by_country": sum_by_group(
                df=dataframe,
                group_field=schema.model.country,
                original_field=schema.model.total_price,
                alias_field=schema.model.revenue
            )
        }

