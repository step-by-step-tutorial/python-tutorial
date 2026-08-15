from __future__ import annotations

from typing import Mapping

from pandas import DataFrame

from dataset.definition import DataWarehouse
from factory import datawarehouse_connection_factory


def truncate_and_populate(datawarehouse: DataWarehouse, dataframe: DataFrame) -> None:
    with datawarehouse_connection_factory.create_connection() as connection:
        for query in datawarehouse.preparing_sql_files.values():
            connection.command(query)

        connection.insert_df(table=datawarehouse.full_table_name, df=dataframe)


def analyze(datawarehouse: DataWarehouse) -> Mapping[str, DataFrame]:
    result = {}

    with datawarehouse_connection_factory.create_connection() as connection:
        for key, query in datawarehouse.analysis_sql_files.items():
            result[key] = connection.query_df(query)

        return result
