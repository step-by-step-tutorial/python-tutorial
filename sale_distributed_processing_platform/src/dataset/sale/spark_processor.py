from collections.abc import Mapping

from pyspark.sql import DataFrame
from pyspark.sql import functions as sf
import dataset.sale.schema as schema
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

        df = remove_duplicates(df, schema.dataset_model_instance.ORDER_ID)
        df = convert_numeric_column(df, schema.dataset_model_instance.QUANTITY, default_value=1.0)
        df = convert_numeric_column(df, schema.dataset_model_instance.UNIT_PRICE)
        df = fill_missing_by_group_average(df, schema.dataset_model_instance.CATEGORY, schema.dataset_model_instance.UNIT_PRICE)
        df = fill_missing_by_column_average(df, schema.dataset_model_instance.UNIT_PRICE)
        df = convert_datetime_column(df, schema.dataset_model_instance.ORDER_DATE)

        df = filter_dataframe(
            df=df,
            conditions=[
                sf.col(schema.dataset_model_instance.ORDER_DATE).isNotNull(),
                sf.col(schema.dataset_model_instance.QUANTITY) > 0,
                sf.col(schema.dataset_model_instance.UNIT_PRICE) >= 0,
            ]
        )

        return df

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        return (
            dataframe
            .withColumn(
                schema.dataset_model_instance.TOTAL_PRICE,
                sf.round(sf.col(schema.dataset_model_instance.QUANTITY) * sf.col(schema.dataset_model_instance.UNIT_PRICE), 2)
            )
            .withColumn(schema.dataset_model_instance.YEAR, sf.year(schema.dataset_model_instance.ORDER_DATE))
            .withColumn(schema.dataset_model_instance.MONTH, sf.month(schema.dataset_model_instance.ORDER_DATE))
        )

    def analyze(self, dataframe: DataFrame) -> Mapping[str, DataFrame]:
        return {
            "revenue_by_category": sum_by_group(
                df=dataframe,
                group_field=schema.dataset_model_instance.CATEGORY,
                original_field=schema.dataset_model_instance.TOTAL_PRICE,
                alias_field=schema.dataset_model_instance.REVENUE
            )
            ,
            "revenue_by_country": sum_by_group(
                df=dataframe,
                group_field=schema.dataset_model_instance.COUNTRY,
                original_field=schema.dataset_model_instance.TOTAL_PRICE,
                alias_field=schema.dataset_model_instance.REVENUE
            )
        }
