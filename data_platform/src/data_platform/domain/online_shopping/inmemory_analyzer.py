from collections.abc import Mapping

from pandas import DataFrame

from data_platform.converter.pandas_converter import sum_by_group
from data_platform.domain.online_shopping.attribute import ONLINE_SHOPPING_ATTRIBUTE as columns
from data_platform.model import DatasetAnalyzer


class InmemoryOnlineShoppingAnalyzer(DatasetAnalyzer[DataFrame]):
    def analyze(self, data: DataFrame) -> Mapping[str, DataFrame]:
        return {
            "revenue_by_country": sum_by_group(data, columns.country, columns.net_revenue, columns.revenue),
            "revenue_by_sales_channel": sum_by_group(data, columns.sales_channel, columns.net_revenue, columns.revenue),
        }
