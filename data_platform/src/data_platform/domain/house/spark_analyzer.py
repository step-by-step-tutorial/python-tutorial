from collections.abc import Mapping

from pyspark.sql import DataFrame

from data_platform.converter.spark_converter import average_by_group
from data_platform.domain.house.attribute import HOUSE_ATTRIBUTE as model
from data_platform.model import DatasetAnalyzer


class SparkHouseAnalyzer(DatasetAnalyzer[DataFrame]):
    def analyze(self, data: DataFrame) -> Mapping[str, DataFrame]:
        return {
            "average_price_by_address": average_by_group(data, model.address, model.price, "average_price"),
            "average_price_per_square_meter_by_room": average_by_group(
                data,
                model.room,
                model.price_per_square_meter,
                "average_price_per_square_meter",
            ),
        }

