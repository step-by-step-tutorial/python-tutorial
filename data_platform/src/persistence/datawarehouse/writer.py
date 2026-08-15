from __future__ import annotations

from collections.abc import Iterable
from itertools import islice
from typing import Any

from connector.datawarehouse import clickhouse_connector as datawarehouse_connection_factory


def _chunk_rows(rows: Iterable[Any], chunk_size: int) -> Iterable[list[Any]]:
    while True:
        chunk = list(islice(rows, chunk_size))
        if not chunk:
            return
        yield chunk


def _insert_rows(rows: list[tuple[Any, ...]], column_names: list[str], table_name: str) -> None:
    connection = datawarehouse_connection_factory.create_connection()
    try:
        connection.insert(table=table_name, data=rows, column_names=column_names)
    finally:
        close = getattr(connection, "close", None)
        if callable(close):
            close()


def write_pandas(datawarehouse: Any, dataframe: Any) -> None:
    table_name = getattr(datawarehouse, "full_table_name")
    _insert_pandas_frame(dataframe, table_name)


def _insert_pandas_frame(dataframe: "pd.DataFrame", table_name: str) -> None:
    import pandas as pd

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("write_pandas expects a pandas DataFrame.")

    connection = datawarehouse_connection_factory.create_connection()
    try:
        connection.insert_df(table=table_name, df=dataframe)
    finally:
        close = getattr(connection, "close", None)
        if callable(close):
            close()


def write_spark(datawarehouse: Any, dataframe: Any) -> None:
    table_name = getattr(datawarehouse, "full_table_name")
    columns = list(dataframe.columns)

    def partition_to_batches(rows: Iterable[Any]) -> Iterable[list[tuple[Any, ...]]]:
        for chunk in _chunk_rows(rows, 1000):
            partition_rows = [
                tuple(
                    (row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)).get(column)
                    for column in columns
                )
                for row in chunk
            ]
            if partition_rows:
                yield partition_rows

    for partition_rows in dataframe.rdd.mapPartitions(partition_to_batches).toLocalIterator():
        _insert_rows(partition_rows, columns, table_name)
