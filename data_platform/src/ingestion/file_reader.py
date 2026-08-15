from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from util.csv_utils import csv_to_dataframe


def read_rows(path: str | Path, consumer: Callable[[dict[str, str]], None]) -> int:
    dataframe = csv_to_dataframe(Path(path))
    for row in dataframe.to_dict(orient="records"):
        consumer(row)

    return len(dataframe)
