from __future__ import annotations

from typing import Any

import pyspark


def row_to_dict(row: Any) -> dict[str, Any]:
    if hasattr(row, "asDict"):
        return row.asDict(recursive=True)
    return dict(row)


def collect_rows(dataframe: pyspark.sql.DataFrame) -> list[tuple[Any, ...]]:
    column_names = list(dataframe.columns)
    rows = []
    for row in dataframe.collect():
        row_dict = row_to_dict(row)
        row_values = tuple(row_dict.get(column) for column in column_names)
        rows.append(row_values)
    return rows


def batch_rows(rows: list[tuple[Any, ...]], batch_size: int = 1000) -> list[list[tuple[Any, ...]]]:
    return [rows[index : index + batch_size] for index in range(0, len(rows), batch_size)]
