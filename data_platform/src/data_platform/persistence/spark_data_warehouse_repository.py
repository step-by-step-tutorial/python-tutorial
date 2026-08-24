from pyspark.sql import DataFrame

from data_platform.model import DataWarehouseEndpoint
from data_platform.persistence import data_warehouse_repository as warehouse_sql
from data_platform.util.collection_utils import batch_of_list
from data_platform.util.spark_utils import dataframe_to_list


class SparkDataWarehouseRepository:
    def __init__(self, endpoint: DataWarehouseEndpoint) -> None:
        self._datawarehouse = endpoint
        self._connection_name = endpoint.connection_name
        self._connection = None

    @property
    def connection(self):
        if self._connection is None:
            self._connection = warehouse_sql.connection_registry.get_item(self._connection_name)
        return self._connection

    def truncate_tables(self) -> None:
        for query_file in self._datawarehouse.truncate_sql_files.values():
            self.connection.command(warehouse_sql.read_text_file(query_file))

    def find_by_queries(self, query_names: list[str]) -> dict[str, object]:
        return {
            query_name: self.connection.query_df(
                warehouse_sql.read_text_file(self._datawarehouse.query_sql_files[query_name]).strip().rstrip(";")
            )
            for query_name in query_names
        }

    def save(self, dataframe: DataFrame) -> None:
        rows = dataframe_to_list(dataframe)
        column_names = list(dataframe.columns)
        for batch in batch_of_list(rows):
            self.connection.insert(table=self._datawarehouse.full_table_name, data=batch, column_names=column_names)

    def replace(self, dataframe: DataFrame) -> None:
        self.truncate_tables()
        self.save(dataframe)

