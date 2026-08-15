import logging
from collections.abc import Mapping

from pandas import DataFrame

from dataset.sale.model import model
from processor.base import DataProcessor
from transformation.inmemory.pandas_ops import (
    remove_duplicates,
    convert_numeric_column,
    fill_missing_by_group_average,
    fill_missing_by_column_average,
    convert_datetime_column,
    reset_index,
    sum_by_group,
)

logger = logging.getLogger(__name__)


class InmemorySaleProcessor(DataProcessor[DataFrame]):
    def clean(self, dataframe: DataFrame) -> DataFrame:
        df = dataframe.copy()

        df = remove_duplicates(df, model.order_id)
        df = convert_numeric_column(df, model.quantity, default_value=1.0)
        df = convert_numeric_column(df, model.unit_price)
        df = fill_missing_by_group_average(df, model.category, model.unit_price)
        df = fill_missing_by_column_average(df, model.unit_price)
        df = convert_datetime_column(df, model.order_date)

        df[model.order_id] = df[model.order_id].astype("int64")
        df[model.quantity] = df[model.quantity].astype("float64")
        df[model.unit_price] = df[model.unit_price].astype("float64")

        if model.total_price in df.columns:
            df[model.total_price] = df[model.total_price].astype("float64")

        df = reset_index(
            df=df,
            conditions=[
                df[model.order_date].notna(),
                df[model.quantity] > 0,
                df[model.unit_price] >= 0,
            ]
        )

        return df

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        df = dataframe.copy()
        df[model.total_price] = (df[model.quantity] * df[model.unit_price]).round(2)
        df[model.year] = df[model.order_date].dt.year
        df[model.month] = df[model.order_date].dt.month
        return df

    def analyze(self, dataframe: DataFrame) -> Mapping[str, DataFrame]:
        result = {
            "revenue_by_category": sum_by_group(
                df=dataframe,
                group_field=model.category,
                original_field=model.total_price,
                alias_field=model.revenue
            ),
            "revenue_by_country": sum_by_group(
                df=dataframe,
                group_field=model.country,
                original_field=model.total_price,
                alias_field=model.revenue
            )
        }
        return result
