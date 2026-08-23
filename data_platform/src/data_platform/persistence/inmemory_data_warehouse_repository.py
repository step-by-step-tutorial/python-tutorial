import pandas

from data_platform.model import DataWarehouseEndpoint
from data_platform.persistence.data_warehouse_repository import DataWarehouseRepository


class InmemoryDataWarehouseRepository(DataWarehouseRepository):
    def __init__(self, endpoint: DataWarehouseEndpoint) -> None:
        super().__init__(endpoint)

    def save(self, dataframe: pandas.DataFrame) -> None:
        self.connection.insert_df(table=self._datawarehouse.full_table_name, df=dataframe)

    def replace(self, dataframe: pandas.DataFrame) -> None:
        self.truncate_tables()
        self.save(dataframe)
