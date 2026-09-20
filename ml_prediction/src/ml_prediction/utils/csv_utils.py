import csv
import logging
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any, TypeVar

import pandas as pd

from ml_prediction.data_model.dict_data import DictData
from ml_prediction.utils.data_validator_utils import is_blank

logger = logging.getLogger(__name__)
T = TypeVar("T")


def write_csv(path: Path, data: Iterable[DictData]) -> None:
    rows = [value.to_dict() for value in data]
    if is_blank(rows):
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=rows[0].keys())
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


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
