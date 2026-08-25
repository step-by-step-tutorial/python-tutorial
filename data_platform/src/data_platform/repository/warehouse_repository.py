import logging

import pandas

from data_platform.model.endpoints import WarehouseEndpoint
from data_platform.registry.connection_registry import connection_registry
from data_platform.util.file_utils import read_text_file

logger = logging.getLogger(__name__)


class WarehouseRepository:
    def __init__(self, warehouse: WarehouseEndpoint) -> None:
        self._warehouse = warehouse
        self._connection_name = warehouse.connection_name
        self._connection = None

    @property
    def connection(self):
        if self._connection is None:
            self._connection = connection_registry.get_item(self._connection_name)
        return self._connection

    def truncate_tables(self) -> None:
        for query_file in self._warehouse.truncate_sql_files.values():
            self.connection.command(read_text_file(query_file))

        logger.info(f"Truncate tables in {self._connection_name}")

    def replace(self, dataframe: pandas.DataFrame) -> None:
        raise NotImplementedError

    def find_by_queries(self, query_names: list[str]) -> dict[str, pandas.DataFrame]:
        result: dict[str, pandas.DataFrame] = {}
        for query_name in query_names:
            query_file = self._warehouse.query_sql_files[query_name]
            query = read_text_file(query_file).strip().rstrip(";")
            result[query_name] = self.connection.query_df(query)

        return result
