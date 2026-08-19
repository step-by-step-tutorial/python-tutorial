from __future__ import annotations

import logging

import pandas
import pyspark

from connector.registry import get_connection
from dataset.definition import DataWarehouseEndpoint
from util.file_utils import read_text_file
from util.spark_utils import batch_of_list, dataframe_to_list

logger = logging.getLogger(__name__)


class DataWarehouseRepository:
    def __init__(self, datawarehouse: DataWarehouseEndpoint) -> None:
        self.datawarehouse = datawarehouse
        self.connection_name = datawarehouse.connection_name

    def truncate_tables(self) -> None:
        connection = get_connection(self.connection_name)
        for query_file in self.datawarehouse.truncate_sql_files.values():
            connection.command(read_text_file(query_file))

        logger.info(f"Truncate tables in {self.connection_name}")

    def populate_table_from_memory(self, dataframe: pandas.DataFrame, table_name: str):
        connection = get_connection(self.connection_name)
        connection.insert_df(table=table_name, df=dataframe)

    def populate_table_from_spark(self, dataframe: pyspark.sql.DataFrame):
        rows = dataframe_to_list(dataframe)
        column_names = list(dataframe.columns)
        connection = get_connection(self.connection_name)
        for batch in batch_of_list(rows):
            connection.insert(table=self.datawarehouse.full_table_name, data=batch, column_names=column_names)

    def truncate_and_populate_from_memory(self, dataframe: pandas.DataFrame) -> None:
        self.truncate_tables()
        self.populate_table_from_memory(dataframe, self.datawarehouse.full_table_name)

    def truncate_and_populate_from_spark(self, dataframe: pyspark.sql.DataFrame) -> None:
        self.truncate_tables()
        self.populate_table_from_spark(dataframe)

    def select_by_queries(self, query_names: list[str]) -> dict[str, pandas.DataFrame]:
        result: dict[str, pandas.DataFrame] = {}
        connection = get_connection(self.connection_name)
        for query_name in query_names:
            query_file = self.datawarehouse.query_sql_files[query_name]
            result[query_name] = connection.query_df(read_text_file(query_file))

        return result
