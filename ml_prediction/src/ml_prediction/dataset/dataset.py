import logging
from pathlib import Path

import pandas as pd

from ml_prediction.utils.csv_utils import load_csv

logger = logging.getLogger(__name__)


class Dataset:
    def __init__(self, path: Path, dataset_name: str) -> None:
        self.path = path
        self.dataset_name = dataset_name

    def training_frame(self, target_column: str) -> pd.DataFrame:
        dataframe = load_csv(self.path).copy()
        dataframe = dataframe.dropna(subset=[target_column])
        logger.info(f"Prepared training frame: rows={len(dataframe)} target={target_column}")
        return dataframe
