from pandas import DataFrame

from data_platform.converter.pandas_converter import convert_datetime_column, convert_numeric_column, remove_duplicates, reset_index
from data_platform.domain.online_shopping.attribute import ONLINE_SHOPPING_ATTRIBUTE as columns
from data_platform.model import DatasetTransformer


class InmemoryOnlineShoppingTransformer(DatasetTransformer[DataFrame]):
    def clean(self, dataframe: DataFrame) -> DataFrame:
        data = remove_duplicates(dataframe.copy(), columns.order_id)
        data = convert_datetime_column(data, columns.order_date)
        data = convert_datetime_column(data, columns.estimated_delivery_date)
        for column in (
            columns.customer_id,
            columns.unit_price,
            columns.quantity,
            columns.subtotal,
            columns.discount_percent,
            columns.shipping_cost,
            columns.tax_amount,
            columns.total_amount,
            columns.delivery_days,
        ):
            data = convert_numeric_column(data, column)

        return reset_index(
            data,
            [
                data[columns.order_id].notna(),
                data[columns.order_date].notna(),
                data[columns.quantity] > 0,
                data[columns.unit_price] >= 0,
                data[columns.total_amount] >= 0,
            ],
        )

    def enrich(self, dataframe: DataFrame) -> DataFrame:
        data = dataframe.copy()
        data[columns.discount_amount] = (data[columns.subtotal] * data[columns.discount_percent] / 100).round(2)
        data[columns.net_revenue] = data[columns.total_amount].round(2)
        data[columns.year] = data[columns.order_date].dt.year
        data[columns.month] = data[columns.order_date].dt.month
        return data
