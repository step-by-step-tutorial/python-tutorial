from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from typing import Any


def find_missing_columns(dataframe: Any, columns: Iterable[str]) -> tuple[str, ...]:
    return tuple(column for column in columns if column not in dataframe.columns)


def row_to_dict(row: Any) -> dict[str, Any]:
    if hasattr(row, "asDict"):
        return row.asDict(recursive=True)
    return dict(row)


def dataframe_to_list(dataframe: Any) -> list[tuple[Any, ...]]:
    column_names = list(dataframe.columns)
    rows = []
    for row in dataframe.collect():
        row_dict = row_to_dict(row)
        rows.append(tuple(row_dict.get(column) for column in column_names))
    return rows


@contextmanager
def persisted_dataframes() -> Iterator[list[Any]]:
    dataframes: list[Any] = []

    try:
        yield dataframes
    finally:
        for dataframe in reversed(dataframes):
            dataframe.unpersist()
