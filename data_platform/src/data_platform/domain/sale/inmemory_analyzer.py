from collections.abc import Mapping

from pandas import DataFrame

from data_platform.domain.sale.attribute import SALE_ATTRIBUTE as model
from data_platform.model import DatasetAnalyzer


class InmemorySaleAnalyzer(DatasetAnalyzer[DataFrame]):
    def analyze(self, data: DataFrame) -> Mapping[str, DataFrame]:
        return {
            "revenue_by_category": data.groupby(model.category, as_index=False)[model.total_price].sum().rename(columns={model.total_price: model.revenue}).sort_values(model.revenue, ascending=False).reset_index(drop=True),
            "revenue_by_country": data.groupby(model.country, as_index=False)[model.total_price].sum().rename(columns={model.total_price: model.revenue}).sort_values(model.revenue, ascending=False).reset_index(drop=True),
        }

