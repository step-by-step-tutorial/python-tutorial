import pandas as pd
from uuid import uuid4

from ml_prediction.config.settings import get_settings
from ml_prediction.data_model.prediction import Prediction
from ml_prediction.dataset.dataset import Dataset
from ml_prediction.inference.predictor import Predictor
from ml_prediction.offline_tracking.report_writer import ReportWriter


class PredictionService:
    def __init__(self, predictor: Predictor[pd.Series], dataset: Dataset) -> None:
        self.settings = get_settings(dataset.dataset_name)
        self.predictor = predictor
        self.dataset = dataset
        self.report_dir = self.settings.report_dir

    def predict(self) -> Prediction:
        model_path = self.predictor.model_path
        dataframe, dataset_path = self.dataset.download()

        report = ReportWriter(
            self.report_dir / f"{self.settings.dataset_name}_prediction_{uuid4()}.csv",
            self.settings.dataset_name,
            "prediction",
            model_path,
        )
        report.record("dataset_ready", details=str(dataset_path))
        report.record("model_loaded", model_path=model_path)

        report.record("dataset_loaded", rows=len(dataframe), details=str(dataset_path))
        predictions = self.predictor.predict(dataframe)
        report.record("predictions_generated", rows=len(predictions), details=f"columns={len(dataframe.columns)}")
        report.record("prediction_completed", details=str(report.path))

        return Prediction(
            dataframe,
            predictions,
            dataset_path,
            report.path,
            self.predictor.prediction_column,
        )
