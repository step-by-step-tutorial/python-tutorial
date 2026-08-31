import pandas as pd

from ml_prediction.config.settings import get_settings
from ml_prediction.data_model.prediction_output import Prediction
from ml_prediction.dataset.dataset import Dataset
from ml_prediction.inference.predictor import Predictor
from ml_prediction.reporting.report_service import ReportService


class PredictionService:
    def __init__(self, predictor: Predictor[pd.Series], dataset: Dataset) -> None:
        self.settings = get_settings(dataset.dataset_name)
        self.predictor = predictor
        self.dataset = dataset
        self.report_service = ReportService(self.settings.report_dir)

    def predict(self) -> Prediction:
        model_path = self.predictor.model_path
        dataframe, dataset_path = self.dataset.download()

        report = self.report_service.start(self.settings.dataset_name, "prediction", model_path)
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
