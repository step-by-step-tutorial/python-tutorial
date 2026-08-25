from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import pandas as pd
import pyspark


def row_to_dict(row: Any) -> dict[str, Any]:
    if hasattr(row, "asDict"):
        return row.asDict(recursive=True)
    return dict(row)


def dataframe_to_list(dataframe: pyspark.sql.DataFrame) -> list[tuple[Any, ...]]:
    column_names = list(dataframe.columns)
    rows = []
    for row in dataframe.collect():
        row_dict = row_to_dict(row)
        row_values = tuple(row_dict.get(column) for column in column_names)
        rows.append(row_values)
    return rows


def empty_compatible_dataframe(dataframe) -> Any:
    return dataframe.limit(0) if isinstance(dataframe, pyspark.sql.DataFrame) else pd.DataFrame()


@contextmanager
def persisted_dataframes() -> Iterator[list[Any]]:
    dataframes: list[Any] = []

    try:
        yield dataframes
    finally:
        for dataframe in reversed(dataframes):
            dataframe.unpersist()
