from collections.abc import Mapping

from pandas import DataFrame

from data_platform.domain.house.attribute import HOUSE_ATTRIBUTE as model
from data_platform.model import DatasetAnalyzer


class InmemoryHouseAnalyzer(DatasetAnalyzer[DataFrame]):
    def analyze(self, data: DataFrame) -> Mapping[str, DataFrame]:
        return {
            "average_price_by_address": data.groupby(model.address, as_index=False)[model.price].mean().rename(columns={model.price: "average_price"}),
            "average_price_by_square_meter": data.groupby(model.room, as_index=False)[model.price_per_square_meter].mean().rename(columns={model.price_per_square_meter: "average_price_by_square_meter"}),
        }

