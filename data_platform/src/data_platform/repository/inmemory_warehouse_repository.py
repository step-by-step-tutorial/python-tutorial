import pandas

from data_platform.model.endpoints import WarehouseEndpoint
from data_platform.repository import warehouse_repository as warehouse_sql


class PandasWarehouseRepository:
    def __init__(self, endpoint: WarehouseEndpoint) -> None:
        self._warehouse = endpoint
        self._connection_name = endpoint.connection_name
        self._connection = None

    @property
    def connection(self):
        if self._connection is None:
            self._connection = warehouse_sql.connection_registry.get_item(self._connection_name)
        return self._connection

    def truncate_tables(self) -> None:
        for query_file in self._warehouse.truncate_sql_files.values():
            self.connection.command(warehouse_sql.read_text_file(query_file))

    def find_by_queries(self, query_names: list[str]) -> dict[str, pandas.DataFrame]:
        return {
            query_name: self.connection.query_df(
                warehouse_sql.read_text_file(self._warehouse.query_sql_files[query_name]).strip().rstrip(";")
            )
            for query_name in query_names
        }

    def save(self, dataframe: pandas.DataFrame) -> None:
        self.connection.insert_df(table=self._warehouse.full_table_name, df=dataframe)

    def replace(self, dataframe: pandas.DataFrame) -> None:
        self.truncate_tables()
        self.save(dataframe)
