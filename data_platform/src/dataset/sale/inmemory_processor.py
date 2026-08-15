import logging
from collections.abc import Mapping

from pandas import DataFrame

from processor.base import DataProcessor
from dataset.sale.model import model
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

        df = remove_duplicates(df, model.ORDER_ID)
        df = convert_numeric_column(df, model.QUANTITY, default_value=1.0)
        df = convert_numeric_column(df, model.UNIT_PRICE)
        df = fill_missing_by_group_average(df, model.CATEGORY, model.UNIT_PRICE)
        df = fill_missing_by_column_average(df, model.UNIT_PRICE)
        df = convert_datetime_column(df, model.ORDER_DATE)

        df[model.ORDER_ID] = df[model.ORDER_ID].astype("int64")
        df[model.QUANTITY] = df[model.QUANTITY].astype("float64")
        df[model.UNIT_PRICE] = df[model.UNIT_PRICE].astype("float64")

        if model.TOTAL_PRICE in df.columns:
            df[model.TOTAL_PRICE] = df[model.TOTAL_PRICE].astype("float64")

        df = reset_index(
            df=df,
            conditions=[
                df[model.ORDER_DATE].notna(),
                df[model.QUANTITY] > 0,
                df[model.UNIT_PRICE] >= 0,
            ]
        )

        return df

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        df = dataframe.copy()
        df[model.TOTAL_PRICE] = (df[model.QUANTITY] * df[model.UNIT_PRICE]).round(2)
        df[model.YEAR] = df[model.ORDER_DATE].dt.year
        df[model.MONTH] = df[model.ORDER_DATE].dt.month
        return df

    def analyze(self, dataframe: DataFrame) -> Mapping[str, DataFrame]:
        result = {
            "revenue_by_category": sum_by_group(
                df=dataframe,
                group_field=model.CATEGORY,
                original_field=model.TOTAL_PRICE,
                alias_field=model.REVENUE
            ),
            "revenue_by_country": sum_by_group(
                df=dataframe,
                group_field=model.COUNTRY,
                original_field=model.TOTAL_PRICE,
                alias_field=model.REVENUE
            )
        }
        return result
