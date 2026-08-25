from data_platform.model import DatasetAnalyzer
from data_platform.persistence.warehouse_repository import WarehouseRepository


class WarehouseSaleAnalyzer(DatasetAnalyzer[WarehouseRepository]):
    def analyze(self, data: WarehouseRepository):
        return data.find_by_queries(["revenue_by_category", "revenue_by_country"])

