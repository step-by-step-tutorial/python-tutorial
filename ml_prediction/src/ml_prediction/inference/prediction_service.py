from uuid import uuid4

import pandas as pd

from ml_prediction.audit.report_event_data import (
    DatasetLoaded, DatasetReady, ModelLoaded, PredictionCompleted,
    PredictionsGenerated,
)
from ml_prediction.audit.report_writer import ReportWriter
from ml_prediction.config.settings import get_settings
from ml_prediction.data_model.prediction import Prediction
from ml_prediction.dataset.dataset import Dataset
from ml_prediction.inference.predictor import Predictor


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
        report.record(DatasetReady(dataset_path))
        report.record(ModelLoaded(model_path))

        report.record(DatasetLoaded(len(dataframe), dataset_path))
        predictions = self.predictor.predict(dataframe)
        report.record(PredictionsGenerated(len(predictions), len(dataframe.columns)))
        report.record(PredictionCompleted(report.path))

        return Prediction(
            dataframe,
            predictions,
            dataset_path,
            report.path,
            self.predictor.prediction_column,
        )
