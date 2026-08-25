from data_platform.model import DatasetAnalyzer
from data_platform.persistence.warehouse_repository import WarehouseRepository


class WarehouseOnlineShoppingAnalyzer(DatasetAnalyzer[WarehouseRepository]):
    def analyze(self, data: WarehouseRepository):
        return data.find_by_queries(["revenue_by_country"])

