from data_platform.model import DatasetAnalyzer
from data_platform.persistence.warehouse_repository import WarehouseRepository


class WarehouseHouseAnalyzer(DatasetAnalyzer[WarehouseRepository]):
    def analyze(self, data: WarehouseRepository):
        return data.find_by_queries(
            ["average_price_by_address", "average_price_per_square_meter_by_room"]
        )

