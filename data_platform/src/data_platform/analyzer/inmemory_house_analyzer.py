from collections.abc import Mapping

from pandas import DataFrame

from data_platform.converter.pandas_converter import average_by_group
from data_platform.model import DatasetAnalyzer
from data_platform.model.house_attribute import HOUSE_ATTRIBUTE as model


class InmemoryHouseAnalyzer(DatasetAnalyzer[DataFrame]):
    def analyze(self, dataframe: DataFrame) -> Mapping[str, DataFrame]:
        return {
            "average_price_by_address": average_by_group(
                dataframe, model.address, model.price, "average_price"
            ),
            "average_price_by_square_meter": average_by_group(
                dataframe, model.room, model.price_per_square_meter, "average_price_by_square_meter"
            ),
        }
