import logging
from collections.abc import Callable
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def csv_to_dataframe(path: str) -> pd.DataFrame:
    if not Path(path).is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")

    logger.info("Reading CSV file from %s", path)

    try:
        df: pd.DataFrame = pd.read_csv(path)
    except Exception as error:
        logger.exception("Failed to read CSV file from %s", path)
        raise ValueError(f"Unable to read CSV file: {path}") from error

    if df.empty:
        raise ValueError(f"CSV file contains no data rows: {path}")

    return df


def read_csv_file(path: str, consumer: Callable[[dict[str, str]], None]) -> int:
    dataframe = csv_to_dataframe(path)
    for row in dataframe.to_dict(orient="records"):
        consumer(row)

    logger.info("Read %s CSV rows from %s", len(dataframe), path)
    return len(dataframe)
