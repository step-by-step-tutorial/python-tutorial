from collections.abc import Mapping

from pyspark.sql import DataFrame

from data_platform.domain.sale.attribute import SALE_ATTRIBUTE as model
from data_platform.model import DatasetAnalyzer


class SparkSaleAnalyzer(DatasetAnalyzer[DataFrame]):
    def analyze(self, data: DataFrame) -> Mapping[str, DataFrame]:
        return {
            "revenue_by_category": data.groupBy(model.category).sum(model.total_price).withColumnRenamed(f"sum({model.total_price})", model.revenue),
            "revenue_by_country": data.groupBy(model.country).sum(model.total_price).withColumnRenamed(f"sum({model.total_price})", model.revenue),
        }

