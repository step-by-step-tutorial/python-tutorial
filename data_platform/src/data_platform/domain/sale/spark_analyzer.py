from collections.abc import Mapping

from pyspark.sql import DataFrame

from data_platform.converter.spark_converter import sum_by_group
from data_platform.domain.sale.attribute import SALE_ATTRIBUTE as model
from data_platform.model import DatasetAnalyzer


class SparkSaleAnalyzer(DatasetAnalyzer[DataFrame]):
    def analyze(self, data: DataFrame) -> Mapping[str, DataFrame]:
        return {
            "revenue_by_category": sum_by_group(data, model.category, model.total_price, model.revenue),
            "revenue_by_country": sum_by_group(data, model.country, model.total_price, model.revenue),
        }

