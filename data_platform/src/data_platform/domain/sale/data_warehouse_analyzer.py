from data_platform.model import DatasetAnalyzer
from data_platform.persistence.data_warehouse_repository import DataWarehouseRepository


class DataWarehouseSaleAnalyzer(DatasetAnalyzer[DataWarehouseRepository]):
    def analyze(self, data: DataWarehouseRepository):
        return data.select_by_queries(["revenue_by_category", "revenue_by_country"])
