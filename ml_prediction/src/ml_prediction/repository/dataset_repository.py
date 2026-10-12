import logging
from pathlib import Path

import pandas as pd

from ml_prediction.config.dataset_source import DatasetSource
from ml_prediction.model.settings_model import SettingsModel
from ml_prediction.repository.datalake_repository import DataLakeRepository
from ml_prediction.util.csv_utils import read_dataframe

logger = logging.getLogger(__name__)


class DatasetRepository:
    def __init__(self, settings: SettingsModel) -> None:
        self._settings = settings

    def load(self) -> tuple[pd.DataFrame, Path]:
        path = self._settings.dataset_path
        if self._settings.dataset_source == DatasetSource.DOWNLOAD:
            DataLakeRepository(self._settings.data_lake).download_latest_partition(path)
        else:
            logger.info("Using local dataset: path=%s", path)
        return read_dataframe(path), path
