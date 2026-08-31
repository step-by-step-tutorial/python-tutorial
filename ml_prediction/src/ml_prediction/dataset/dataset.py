import logging
from pathlib import Path

import pandas as pd

from ml_prediction.config.settings import DatasetSource, get_settings
from ml_prediction.repository.datalake_repository import DataLakeRepository
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

    def download(self) -> tuple[pd.DataFrame, Path]:
        settings = get_settings(self.dataset_name)
        if settings.dataset_source == DatasetSource.DOWNLOAD:
            DataLakeRepository(self.dataset_name).download_latest_csv(self.path)
        else:
            logger.info("Using local dataset: path=%s", self.path)
        return load_csv(self.path), self.path
