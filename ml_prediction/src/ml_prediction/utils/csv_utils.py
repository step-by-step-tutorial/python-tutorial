import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def load_csv(path: Path) -> pd.DataFrame:
    logger.info("Loading dataset: path=%s", path)
    try:
        dataframe = pd.read_csv(path)
    except pd.errors.EmptyDataError as error:
        raise ValueError("Dataset must not be empty") from error
    logger.info("Dataset loaded: rows=%s columns=%s", len(dataframe), len(dataframe.columns))
    return dataframe
