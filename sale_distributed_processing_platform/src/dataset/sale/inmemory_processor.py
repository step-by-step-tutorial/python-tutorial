import logging
from collections.abc import Mapping

from pandas import DataFrame

import dataset.sale.schema as schema
from dataset.definition import DataProcessor
from util.pandas_dataframe_utils import (
    remove_duplicates,
    convert_numeric_column,
    fill_missing_by_group_average,
    fill_missing_by_column_average,
    convert_datetime_column,
    reset_index, sum_by_group
)

logger = logging.getLogger(__name__)


class InmemorySaleProcessor(DataProcessor[DataFrame]):
    def clean(self, dataframe: DataFrame) -> DataFrame:
        logger.info("Start cleaning data")
        df = dataframe.copy()

        df = remove_duplicates(df, schema.dataset_model_instance.ORDER_ID)
        df = convert_numeric_column(df, schema.dataset_model_instance.QUANTITY, default_value=1.0)
        df = convert_numeric_column(df, schema.dataset_model_instance.UNIT_PRICE)
        df = fill_missing_by_group_average(df, schema.dataset_model_instance.CATEGORY,
                                           schema.dataset_model_instance.UNIT_PRICE)
        df = fill_missing_by_column_average(df, schema.dataset_model_instance.UNIT_PRICE)
        df = convert_datetime_column(df, schema.dataset_model_instance.ORDER_DATE)

        df[schema.dataset_model_instance.ORDER_ID] = df[schema.dataset_model_instance.ORDER_ID].astype("int64")
        df[schema.dataset_model_instance.QUANTITY] = df[schema.dataset_model_instance.QUANTITY].astype("float64")
        df[schema.dataset_model_instance.UNIT_PRICE] = df[schema.dataset_model_instance.UNIT_PRICE].astype("float64")

        if schema.dataset_model_instance.TOTAL_PRICE in df.columns:
            df[schema.dataset_model_instance.TOTAL_PRICE] = df[schema.dataset_model_instance.TOTAL_PRICE].astype(
                "float64")

        df = reset_index(
            df=df,
            conditions=[
                df[schema.dataset_model_instance.ORDER_DATE].notna(),
                df[schema.dataset_model_instance.QUANTITY] > 0,
                df[schema.dataset_model_instance.UNIT_PRICE] >= 0,
            ]
        )

        logger.info("Finish cleaning data")

        return df

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        logger.info("Start enriching data")
        df = dataframe.copy()
        df[schema.dataset_model_instance.TOTAL_PRICE] = (
                df[schema.dataset_model_instance.QUANTITY] * df[schema.dataset_model_instance.UNIT_PRICE]).round(2)
        df[schema.dataset_model_instance.YEAR] = df[schema.dataset_model_instance.ORDER_DATE].dt.year
        df[schema.dataset_model_instance.MONTH] = df[schema.dataset_model_instance.ORDER_DATE].dt.month
        logger.info("Finish enriching data")
        return df

    def analyze(self, dataframe: DataFrame) -> Mapping[str, DataFrame]:
        logger.info("Start analyzing data")
        result = {
            "revenue_by_category": sum_by_group(
                df=dataframe,
                group_field=schema.dataset_model_instance.CATEGORY,
                original_field=schema.dataset_model_instance.TOTAL_PRICE,
                alias_field=schema.dataset_model_instance.REVENUE
            ),
            "revenue_by_country": sum_by_group(
                df=dataframe,
                group_field=schema.dataset_model_instance.COUNTRY,
                original_field=schema.dataset_model_instance.TOTAL_PRICE,
                alias_field=schema.dataset_model_instance.REVENUE
            )
        }
        logger.info("Finish analyzing data")
        return result
