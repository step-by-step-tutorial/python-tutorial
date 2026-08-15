from __future__ import annotations

from collections.abc import Mapping

from pandas import DataFrame

from connector.datawarehouse import clickhouse_connector as datawarehouse_connection_factory
from dataset.definition import DataWarehouseEndpoint
from util.file_utils import read_text_file


def truncate_and_populate(datawarehouse: DataWarehouseEndpoint, dataframe: DataFrame) -> None:
    with datawarehouse_connection_factory.create_connection() as connection:
        for query_file in datawarehouse.preparing_sql_files.values():
            query = read_text_file(query_file)
            connection.command(query)

        if hasattr(dataframe, "foreachPartition"):
            from persistence.datawarehouse.writer import write_spark

            write_spark(datawarehouse, dataframe)
            return

        connection.insert_df(table=datawarehouse.full_table_name, df=dataframe)


def analyze(datawarehouse: DataWarehouseEndpoint) -> Mapping[str, DataFrame]:
    result = {}

    with datawarehouse_connection_factory.create_connection() as connection:
        for key, query_file in datawarehouse.analysis_sql_files.items():
            query = read_text_file(query_file)
            result[key] = connection.query_df(query)

        return result
