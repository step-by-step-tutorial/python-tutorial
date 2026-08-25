from pandas import DataFrame

from data_platform.model.endpoints import WarehouseEndpoint
from data_platform.registry.connection_registry import connection_registry
from data_platform.util.file_utils import read_text_file


class InmemoryWarehouseRepository:
    def __init__(self, endpoint: WarehouseEndpoint) -> None:
        self._endpoint = endpoint
        self._connection_name = endpoint.connection_name

    def truncate_tables(self) -> None:
        for sql_file in self._endpoint.truncate_sql_files.values():
            connection = connection_registry.get_item(self._connection_name)
            connection.command(read_text_file(sql_file))

    def write(self, dataframe: DataFrame) -> None:
        connection = connection_registry.get_item(self._connection_name)
        connection.insert_df(table=self._endpoint.full_table_name, df=dataframe)

    def overwrite(self, dataframe: DataFrame) -> None:
        self.truncate_tables()
        self.write(dataframe)
