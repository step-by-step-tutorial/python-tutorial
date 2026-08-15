from collections.abc import Iterator
from contextlib import contextmanager

from pyspark.sql import DataFrame


@contextmanager
def persisted_dataframes() -> Iterator[list[DataFrame]]:
    dataframes: list[DataFrame] = []

    try:
        yield dataframes
    finally:
        for dataframe in reversed(dataframes):
            dataframe.unpersist()
