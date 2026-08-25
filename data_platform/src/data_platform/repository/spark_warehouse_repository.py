from pyspark.sql import DataFrame

from data_platform.model.endpoints import WarehouseEndpoint
from data_platform.registry.connection_registry import connection_registry
from data_platform.util.collection_utils import to_batches
from data_platform.util.dataframe_utils import dataframe_to_list
from data_platform.util.file_utils import read_text_file


class SparkWarehouseRepository:
    def __init__(self, endpoint: WarehouseEndpoint) -> None:
        self._endpoint = endpoint
        self._connection_name = endpoint.connection_name

    def truncate_tables(self) -> None:
        for query_file in self._endpoint.truncate_sql_files.values():
            connection = connection_registry.get_item(self._connection_name)
            connection.command(read_text_file(query_file))

    def write(self, dataframe: DataFrame) -> None:
        rows = dataframe_to_list(dataframe)
        column_names = list(dataframe.columns)
        for batch in to_batches(rows):
            connection = connection_registry.get_item(self._connection_name)
            connection.insert(table=self._endpoint.full_table_name, data=batch, column_names=column_names)

    def overwrite(self, dataframe: DataFrame) -> None:
        self.truncate_tables()
        self.write(dataframe)
