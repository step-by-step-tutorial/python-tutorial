from data_platform.model import DatasetAnalyzer
from data_platform.persistence.data_warehouse_repository import DataWarehouseRepository


class DataWarehouseHouseAnalyzer(DatasetAnalyzer[DataWarehouseRepository]):
    def analyze(self, data: DataWarehouseRepository):
        return data.find_by_queries(
            ["average_price_by_address", "average_price_per_square_meter_by_room"]
        )
