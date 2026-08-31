from typing import Any

from ml_prediction.config.settings import get_settings
from ml_prediction.dataset.dataset import Dataset
from ml_prediction.evaluation.experiment_comparison_service import ExperimentComparisonService
from ml_prediction.data_model.prediction_output import PredictionOutput
from ml_prediction.inference.prediction_service import PredictionService
from ml_prediction.inference.predictor import Predictor
from ml_prediction.training.trainer import Trainer


class Application:
    def __init__(self, dataset: Dataset, trainer: Trainer[Any], predictor: Predictor[Any] | None) -> None:
        self.dataset = dataset
        self.settings = get_settings(dataset.dataset_name)
        self.trainer = trainer
        self.prediction_service = PredictionService(predictor, dataset) if predictor is not None else None
        self.experiment_comparison_service = ExperimentComparisonService(dataset.dataset_name)

    def train(self) -> Any:
        return self.trainer.train()

    def predict(self) -> PredictionOutput:
        if self.prediction_service is None:
            raise RuntimeError("Prediction service is not configured for this application")
        return self.prediction_service.predict()
