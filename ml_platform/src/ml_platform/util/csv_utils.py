import csv
import logging
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from typing import Any, TypeVar

import pandas as pd

logger = logging.getLogger(__name__)
T = TypeVar("T")


def append_rows(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    rows = list(rows)
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0]))
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


def read_rows(path: Path, converter: Callable[[dict[str, str]], T]) -> list[T]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as csv_file:
        return [converter(row) for row in csv.DictReader(csv_file)]


def read_dataframe(path: Path) -> pd.DataFrame:
    try:
        dataframe = pd.read_csv(path)
    except pd.errors.EmptyDataError as error:
        raise ValueError(f"Dataset is empty: path={path}") from error
    logger.info("Loaded dataset: path=%s rows=%s columns=%s", path, len(dataframe), len(dataframe.columns))
    return dataframe
