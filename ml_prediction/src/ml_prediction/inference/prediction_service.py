import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ml_prediction.config.settings import AppSettings
from ml_prediction.dataset.dataset import Dataset
from ml_prediction.inference.predictor import Predictor
from ml_prediction.repository.datalake_repository import DataLakeRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PredictionOutput:
    dataframe: pd.DataFrame
    predictions: pd.Series
    source_path: Path


class PredictionService:
    def __init__(
            self,
            settings: AppSettings,
            predictor: Predictor[pd.Series],
            dataset: Dataset,
    ) -> None:
        self.settings = settings
        self.predictor = predictor
        self.dataset = dataset
        self.repository = DataLakeRepository(settings.data_lake)

    def predict(self) -> PredictionOutput:
        dataset_path = self.download_dataset()
        if self.dataset.path != dataset_path:
            raise ValueError(f"Dataset path does not match downloaded path: {self.dataset.path}")
        dataframe = self.dataset.load()
        predictions = self.predictor.predict(dataframe)
        return PredictionOutput(dataframe, predictions, dataset_path)

    def download_dataset(self) -> Path:
        dataset_path = self.settings.data_dir / "house.csv"
        self.repository.download_latest_csv(dataset_path)
        return dataset_path
