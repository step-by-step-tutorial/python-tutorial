import logging
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

