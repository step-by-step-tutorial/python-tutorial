from pyspark.sql import DataFrame

from data_platform.model import DataWarehouseEndpoint
from data_platform.persistence.data_warehouse_repository import DataWarehouseRepository
from data_platform.util.collection_utils import batch_of_list
from data_platform.util.spark_utils import dataframe_to_list


class SparkDataWarehouseRepository(DataWarehouseRepository):
    def __init__(self, endpoint: DataWarehouseEndpoint) -> None:
        super().__init__(endpoint)

    def save(self, dataframe: DataFrame) -> None:
        rows = dataframe_to_list(dataframe)
        column_names = list(dataframe.columns)
        for batch in batch_of_list(rows):
            self.connection.insert(table=self._datawarehouse.full_table_name, data=batch, column_names=column_names)

    def replace(self, dataframe: DataFrame) -> None:
        self.truncate_tables()
        self.save(dataframe)

