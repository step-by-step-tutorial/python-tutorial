from collections.abc import Mapping

from pyspark.sql import DataFrame
from pyspark.sql import functions as sf
import dataset.sale.model as schema
from dataset.definition import DataProcessor
from util.spark_dataframe_utils import (
    remove_duplicates,
    convert_numeric_column,
    fill_missing_by_group_average,
    fill_missing_by_column_average,
    convert_datetime_column,
    filter_dataframe,
    sum_by_group,
)


class SparkSaleProcessor(DataProcessor[DataFrame]):
    def clean(self, dataframe: DataFrame) -> DataFrame:
        df = dataframe

        df = remove_duplicates(df, schema.model.ORDER_ID)
        df = convert_numeric_column(df, schema.model.QUANTITY, default_value=1.0)
        df = convert_numeric_column(df, schema.model.UNIT_PRICE)
        df = fill_missing_by_group_average(df, schema.model.CATEGORY, schema.model.UNIT_PRICE)
        df = fill_missing_by_column_average(df, schema.model.UNIT_PRICE)
        df = convert_datetime_column(df, schema.model.ORDER_DATE)

        df = filter_dataframe(
            df=df,
            conditions=[
                sf.col(schema.model.ORDER_DATE).isNotNull(),
                sf.col(schema.model.QUANTITY) > 0,
                sf.col(schema.model.UNIT_PRICE) >= 0,
            ]
        )

        return df

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        return (
            dataframe
            .withColumn(
                schema.model.TOTAL_PRICE,
                sf.round(sf.col(schema.model.QUANTITY) * sf.col(schema.model.UNIT_PRICE), 2)
            )
            .withColumn(schema.model.YEAR, sf.year(schema.model.ORDER_DATE))
            .withColumn(schema.model.MONTH, sf.month(schema.model.ORDER_DATE))
        )

    def analyze(self, dataframe: DataFrame) -> Mapping[str, DataFrame]:
        return {
            "revenue_by_category": sum_by_group(
                df=dataframe,
                group_field=schema.model.CATEGORY,
                original_field=schema.model.TOTAL_PRICE,
                alias_field=schema.model.REVENUE
            )
            ,
            "revenue_by_country": sum_by_group(
                df=dataframe,
                group_field=schema.model.COUNTRY,
                original_field=schema.model.TOTAL_PRICE,
                alias_field=schema.model.REVENUE
            )
        }
