import logging
from pathlib import Path

import pandas as pd

from ml_prediction.config.settings import get_settings
from ml_prediction.data_model.app_settings import DatasetSource
from ml_prediction.data_model.prediction_output import PredictionOutput
from ml_prediction.dataset.dataset import Dataset
from ml_prediction.inference.predictor import Predictor
from ml_prediction.reporting.report_service import ReportService
from ml_prediction.repository.datalake_repository import DataLakeRepository
from ml_prediction.utils.csv_utils import load_csv

logger = logging.getLogger(__name__)


class PredictionService:
    def __init__(
            self,
            predictor: Predictor[pd.Series],
            dataset: Dataset,
    ) -> None:
        self.settings = get_settings(dataset.dataset_name)
        self.predictor = predictor
        self.dataset = dataset
        self.datalake_repository = DataLakeRepository(dataset.dataset_name)
        self.report_service = ReportService(self.settings.report_dir)

    def predict(self) -> PredictionOutput:
        model_path = self.predictor.model_path
        if not isinstance(model_path, Path):
            model_path = None
        report = self.report_service.start(self.settings.dataset_name, "prediction", model_path)
        dataset_path = self.download_dataset()
        report.record("dataset_ready", details=str(dataset_path))
        report.record("model_loaded", model_path=self.predictor.model_path)
        if self.dataset.path != dataset_path:
            raise ValueError(f"Dataset path does not match downloaded path: {self.dataset.path}")
        dataframe = load_csv(self.dataset.path)
        report.record("dataset_loaded", rows=len(dataframe), details=str(dataset_path))
        predictions = self.predictor.predict(dataframe)
        report.record("predictions_generated", rows=len(predictions), details=f"columns={len(dataframe.columns)}")
        report.record("prediction_completed", details=str(report.path))
        return PredictionOutput(
            dataframe,
            predictions,
            dataset_path,
            report.path,
            self.predictor.prediction_column,
        )

    def download_dataset(self) -> Path:
        dataset_path = self.settings.data_dir / self.settings.dataset_filename
        if self.settings.dataset_source == DatasetSource.DOWNLOAD:
            self.datalake_repository.download_latest_csv(dataset_path)
        else:
            logger.info("Using local dataset: path=%s", dataset_path)
        return dataset_path
