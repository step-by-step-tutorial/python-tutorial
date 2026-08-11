import logging
from collections.abc import Mapping

from pandas import DataFrame

from dataset.definition import DataProcessor
from dataset.sale.schema import dataset_model_instance as model_instance
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
        df = dataframe.copy()

        df = remove_duplicates(df, model_instance.ORDER_ID)
        df = convert_numeric_column(df, model_instance.QUANTITY, default_value=1.0)
        df = convert_numeric_column(df, model_instance.UNIT_PRICE)
        df = fill_missing_by_group_average(df, model_instance.CATEGORY, model_instance.UNIT_PRICE)
        df = fill_missing_by_column_average(df, model_instance.UNIT_PRICE)
        df = convert_datetime_column(df, model_instance.ORDER_DATE)

        df[model_instance.ORDER_ID] = df[model_instance.ORDER_ID].astype("int64")
        df[model_instance.QUANTITY] = df[model_instance.QUANTITY].astype("float64")
        df[model_instance.UNIT_PRICE] = df[model_instance.UNIT_PRICE].astype("float64")

        if model_instance.TOTAL_PRICE in df.columns:
            df[model_instance.TOTAL_PRICE] = df[model_instance.TOTAL_PRICE].astype("float64")

        df = reset_index(
            df=df,
            conditions=[
                df[model_instance.ORDER_DATE].notna(),
                df[model_instance.QUANTITY] > 0,
                df[model_instance.UNIT_PRICE] >= 0,
            ]
        )

        return df

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        df = dataframe.copy()
        df[model_instance.TOTAL_PRICE] = (df[model_instance.QUANTITY] * df[model_instance.UNIT_PRICE]).round(2)
        df[model_instance.YEAR] = df[model_instance.ORDER_DATE].dt.year
        df[model_instance.MONTH] = df[model_instance.ORDER_DATE].dt.month
        return df

    def analyze(self, dataframe: DataFrame) -> Mapping[str, DataFrame]:
        result = {
            "revenue_by_category": sum_by_group(
                df=dataframe,
                group_field=model_instance.CATEGORY,
                original_field=model_instance.TOTAL_PRICE,
                alias_field=model_instance.REVENUE
            ),
            "revenue_by_country": sum_by_group(
                df=dataframe,
                group_field=model_instance.COUNTRY,
                original_field=model_instance.TOTAL_PRICE,
                alias_field=model_instance.REVENUE
            )
        }
        return result
