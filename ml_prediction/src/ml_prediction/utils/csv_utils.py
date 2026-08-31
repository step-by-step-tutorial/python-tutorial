import logging
import csv
from collections.abc import Callable, Collection, Iterable
from pathlib import Path
from typing import Any, TypeVar

import pandas as pd

logger = logging.getLogger(__name__)
T = TypeVar("T")


def write_csv(
        path: Path,
        data: Iterable[Any],
        fieldnames: Collection[str],
        converter: Callable[[Any], dict[str, str]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        for row in data:
            writer.writerow(converter(row))


def read_csv(path: Path, converter: Callable[[dict[str, str]], T]) -> list[T]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as csv_file:
        return [converter(row) for row in csv.DictReader(csv_file)]


def load_csv(path: Path) -> pd.DataFrame:
    logger.info("Loading dataset: path=%s", path)
    try:
        dataframe = pd.read_csv(path)
    except pd.errors.EmptyDataError as error:
        raise ValueError("Dataset must not be empty") from error
    logger.info("Dataset loaded: rows=%s columns=%s", len(dataframe), len(dataframe.columns))
    return dataframe
