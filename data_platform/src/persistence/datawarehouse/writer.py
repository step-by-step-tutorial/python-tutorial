from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd

from connector.datawarehouse import clickhouse_connector as datawarehouse_connection_factory
from dataset.definition import DataWarehouseEndpoint


def _insert_pandas_frame(dataframe: pd.DataFrame, table_name: str) -> None:
    with datawarehouse_connection_factory.create_connection() as connection:
        connection.insert_df(table=table_name, df=dataframe)


def write_pandas(datawarehouse: DataWarehouseEndpoint, dataframe: pd.DataFrame) -> None:
    _insert_pandas_frame(dataframe, datawarehouse.full_table_name)


def write_spark(datawarehouse: DataWarehouseEndpoint, dataframe: Any) -> None:
    columns = list(dataframe.columns)

    def write_partition(rows: Iterable[Any]) -> None:
        partition_rows = [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows]
        if not partition_rows:
            return

        pdf = pd.DataFrame(partition_rows, columns=columns)
        _insert_pandas_frame(pdf, datawarehouse.full_table_name)

    dataframe.foreachPartition(write_partition)
