from __future__ import annotations

import pandas
import pyspark

from connector.datawarehouse_connection_factory import get_connection
from dataset.definition import DataWarehouseEndpoint
from util.file_utils import read_text_file
from util.spark_utils import batch_of_list, dataframe_to_list


class DataWarehouseRepository:
    def __init__(self, datawarehouse: DataWarehouseEndpoint) -> None:
        self.datawarehouse = datawarehouse
        self.connection_name = datawarehouse.connection_name

    def truncate_tables(self) -> None:
        connection = get_connection(self.connection_name)
        for query_file in self.datawarehouse.truncate_sql_files.values():
            connection.command(read_text_file(query_file))

    def truncate_and_populate_from_memory(self, dataframe: pandas.DataFrame) -> None:
        connection = get_connection(self.connection_name)
        for query_file in self.datawarehouse.truncate_sql_files.values():
            connection.command(read_text_file(query_file))
        connection.insert_df(table=self.datawarehouse.full_table_name, df=dataframe)

    def truncate_and_populate_from_spark(self, dataframe: pyspark.sql.DataFrame) -> None:
        connection = get_connection(self.connection_name)
        for query_file in self.datawarehouse.truncate_sql_files.values():
            connection.command(read_text_file(query_file))
        rows = dataframe_to_list(dataframe)
        column_names = list(dataframe.columns)
        for batch in batch_of_list(rows):
            connection.insert(table=self.datawarehouse.full_table_name, data=batch, column_names=column_names)

    def analyze(self, query_names: list[str]) -> dict[str, pandas.DataFrame]:
        result: dict[str, pandas.DataFrame] = {}
        connection = get_connection(self.connection_name)
        for query_name in query_names:
            query_file = self.datawarehouse.query_sql_files[query_name]
            result[query_name] = connection.query_df(read_text_file(query_file))

        return result
