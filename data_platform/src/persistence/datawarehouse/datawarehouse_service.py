from __future__ import annotations

from collections.abc import Mapping

import pandas
import pyspark

from connector.datawarehouse import clickhouse_connector as datawarehouse_connection_factory
from dataset.definition import DataWarehouseEndpoint
from util.file_utils import read_text_file
from util.spark_utils import batch_rows, collect_rows


def truncate_tables(datawarehouse: DataWarehouseEndpoint, connection) -> None:
    for query_file in datawarehouse.preparing_sql_files.values():
        connection.command(read_text_file(query_file))


def truncate_and_populate_from_pandas(datawarehouse: DataWarehouseEndpoint, dataframe: pandas.DataFrame) -> None:
    with datawarehouse_connection_factory.create_connection() as connection:
        truncate_tables(datawarehouse, connection)
        connection.insert_df(table=datawarehouse.full_table_name, df=dataframe)


def truncate_and_populate_from_spark(datawarehouse: DataWarehouseEndpoint, dataframe: pyspark.sql.DataFrame) -> None:
    with datawarehouse_connection_factory.create_connection() as connection:
        truncate_tables(datawarehouse, connection)
        rows = collect_rows(dataframe)
        column_names = list(dataframe.columns)
        for batch in batch_rows(rows):
            connection.insert(table=datawarehouse.full_table_name, data=batch, column_names=column_names)


def analyze(datawarehouse: DataWarehouseEndpoint) -> Mapping[str, pandas.DataFrame]:
    result = {}

    with datawarehouse_connection_factory.create_connection() as connection:
        for key, query_file in datawarehouse.analysis_sql_files.items():
            result[key] = connection.query_df(read_text_file(query_file))

        return result
