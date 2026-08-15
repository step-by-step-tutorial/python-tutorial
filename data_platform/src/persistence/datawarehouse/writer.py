from __future__ import annotations

from collections.abc import Iterable
from itertools import islice
from typing import Any

import pandas as pd

from connector.datawarehouse import clickhouse_connector as datawarehouse_connection_factory
from dataset.definition import DataWarehouseEndpoint


def _chunk_rows(rows: Iterable[Any], chunk_size: int) -> Iterable[list[Any]]:
    while True:
        chunk = list(islice(rows, chunk_size))
        if not chunk:
            return
        yield chunk


def _insert_pandas_frame(dataframe: pd.DataFrame, table_name: str) -> None:
    connection = datawarehouse_connection_factory.create_connection()
    try:
        connection.insert_df(table=table_name, df=dataframe)
    finally:
        close = getattr(connection, "close", None)
        if callable(close):
            close()


def write_pandas(datawarehouse: DataWarehouseEndpoint, dataframe: pd.DataFrame) -> None:
    _insert_pandas_frame(dataframe, datawarehouse.full_table_name)


def write_spark(datawarehouse: DataWarehouseEndpoint, dataframe: Any) -> None:
    columns = list(dataframe.columns)

    def write_partition(rows: Iterable[Any]) -> None:
        for chunk in _chunk_rows(rows, 1000):
            partition_rows = [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in chunk]
            if not partition_rows:
                continue

            pdf = pd.DataFrame(partition_rows, columns=columns)
            _insert_pandas_frame(pdf, datawarehouse.full_table_name)

    dataframe.foreachPartition(write_partition)
