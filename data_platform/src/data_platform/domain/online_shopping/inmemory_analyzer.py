from collections.abc import Mapping

from pandas import DataFrame

from data_platform.domain.online_shopping.attribute import ONLINE_SHOPPING_ATTRIBUTE as columns
from data_platform.model import DatasetAnalyzer


class InmemoryOnlineShoppingAnalyzer(DatasetAnalyzer[DataFrame]):
    def analyze(self, data: DataFrame) -> Mapping[str, DataFrame]:
        return {
            "revenue_by_country": data.groupby(columns.country, as_index=False)[columns.net_revenue].sum().rename(columns={columns.net_revenue: columns.revenue}).sort_values(columns.revenue, ascending=False).reset_index(drop=True),
            "revenue_by_sales_channel": data.groupby(columns.sales_channel, as_index=False)[columns.net_revenue].sum().rename(columns={columns.net_revenue: columns.revenue}).sort_values(columns.revenue, ascending=False).reset_index(drop=True),
        }

