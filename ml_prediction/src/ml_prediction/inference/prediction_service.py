import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ml_prediction.config.settings import AppSettings, DatasetSource
from ml_prediction.dataset.dataset import Dataset
from ml_prediction.inference.predictor import Predictor
from ml_prediction.repository.datalake_repository import DataLakeRepository
from ml_prediction.reporting.report_service import ReportService

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PredictionOutput:
    dataframe: pd.DataFrame
    predictions: pd.Series
    source_path: Path
    report_path: Path | None = None


class PredictionService:
    def __init__(
            self,
            settings: AppSettings,
            predictor: Predictor[pd.Series],
            dataset: Dataset,
            report_service: ReportService | None = None,
    ) -> None:
        self.settings = settings
        self.predictor = predictor
        self.dataset = dataset
        self.report_service = report_service or ReportService(settings.report_dir)
        self.repository = DataLakeRepository(settings.data_lake)

    def predict(self) -> PredictionOutput:
        report = self.report_service.start("house", "prediction")
        dataset_path = self.download_dataset()
        report.record("dataset_ready", details=str(dataset_path))
        if self.dataset.path != dataset_path:
            raise ValueError(f"Dataset path does not match downloaded path: {self.dataset.path}")
        dataframe = self.dataset.load()
        report.record("dataset_loaded", rows=len(dataframe), details=str(dataset_path))
        predictions = self.predictor.predict(dataframe)
        report.record("predictions_generated", rows=len(predictions), details=f"columns={len(dataframe.columns)}")
        report.record("prediction_completed", details=str(report.path))
        return PredictionOutput(dataframe, predictions, dataset_path, report.path)

    def download_dataset(self) -> Path:
        dataset_path = self.settings.data_dir / "house.csv"
        if self.settings.dataset_source == DatasetSource.DOWNLOAD:
            self.repository.download_latest_csv(dataset_path)
        else:
            logger.info("Using local dataset: path=%s", dataset_path)
        return dataset_path
