from __future__ import annotations

import pandas
import pyspark

from dataset.definition import DataWarehouseEndpoint
from util.file_utils import read_text_file
from util.spark_utils import batch_of_list, dataframe_to_list


class DataWarehouseRepository:
    def __init__(self, datawarehouse: DataWarehouseEndpoint) -> None:
        self.datawarehouse = datawarehouse
        self.connection_name = datawarehouse.connection_name

    def _truncate_tables(self, connection) -> None:
        for query_file in self.datawarehouse.truncate_sql_files.values():
            connection.command(read_text_file(query_file))

    def truncate_tables(self) -> None:
        from connector.datawarehouse_connection_factory import get_connection

        connection = get_connection(self.connection_name)
        self._truncate_tables(connection)

    def truncate_and_populate_from_memory(self, dataframe: pandas.DataFrame) -> None:
        from connector.datawarehouse_connection_factory import get_connection

        connection = get_connection(self.connection_name)
        self._truncate_tables(connection)
        connection.insert_df(table=self.datawarehouse.full_table_name, df=dataframe)

    def collect_rows(self, dataframe: pyspark.sql.DataFrame) -> list[tuple[object, ...]]:
        return dataframe_to_list(dataframe)

    def batch_rows(self, rows: list[tuple[object, ...]], batch_size: int = 1000) -> list[list[tuple[object, ...]]]:
        return batch_of_list(rows, batch_size=batch_size)

    def truncate_and_populate_from_spark(self, dataframe: pyspark.sql.DataFrame) -> None:
        from connector.datawarehouse_connection_factory import get_connection

        connection = get_connection(self.connection_name)
        self._truncate_tables(connection)
        rows = self.collect_rows(dataframe)
        column_names = list(dataframe.columns)
        for batch in self.batch_rows(rows):
            connection.insert(table=self.datawarehouse.full_table_name, data=batch, column_names=column_names)

    def analyze(self) -> dict[str, pandas.DataFrame]:
        result: dict[str, pandas.DataFrame] = {}
        from connector.datawarehouse_connection_factory import get_connection

        connection = get_connection(self.connection_name)
        for key, query_file in self.datawarehouse.query_sql_files.items():
            result[key] = connection.query_df(read_text_file(query_file))

        return result
