from collections.abc import Mapping

from pyspark.sql import DataFrame

from data_platform.domain.house.attribute import HOUSE_ATTRIBUTE as model
from data_platform.model import DatasetAnalyzer


class SparkHouseAnalyzer(DatasetAnalyzer[DataFrame]):
    def analyze(self, data: DataFrame) -> Mapping[str, DataFrame]:
        return {
            "average_price_by_address": data.groupBy(model.address).avg(model.price).withColumnRenamed(f"avg({model.price})", "average_price"),
            "average_price_per_square_meter_by_room": data.groupBy(model.room).avg(model.price_per_square_meter).withColumnRenamed(f"avg({model.price_per_square_meter})", "average_price_per_square_meter"),
        }

