import logging
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError

logger = logging.getLogger(__name__)


def csv_to_dataframe(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")

    logger.info("Reading CSV file from %s", path)

    try:
        df: pd.DataFrame = pd.read_csv(path)
    except EmptyDataError as error:
        raise ValueError(f"CSV file is empty: {path}") from error
    except pd.errors.ParserError as error:
        raise ValueError(f"CSV file is invalid: {path}") from error

    if df.empty:
        raise ValueError(f"CSV file contains no data rows: {path}")

    return df
