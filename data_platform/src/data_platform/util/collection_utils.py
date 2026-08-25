from collections.abc import Iterable
from collections.abc import Mapping
from typing import Any


def list_of_values(map: Mapping) -> list[str]:
    return [str(item) for item in map.values()]


def batch_of_list(rows: list[tuple[object, ...]], batch_size: int = 1000) -> list[list[tuple[object, ...]]]:
    return [rows[index: index + batch_size] for index in range(0, len(rows), batch_size)]


def find_missing_columns(dataframe: Any, columns: Iterable[str]) -> tuple[str, ...]:
    return tuple(column for column in columns if column not in dataframe.attribute)
