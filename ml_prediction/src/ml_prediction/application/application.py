from typing import Any

from ml_prediction.config.settings import AppSettings
from ml_prediction.evaluation.experiment_comparison_service import ExperimentComparisonService
from ml_prediction.inference.prediction_service import PredictionOutput
from ml_prediction.inference.prediction_service import PredictionService
from ml_prediction.training.trainer import Trainer


class Application:
    def __init__(
            self,
            settings: AppSettings,
            trainer: Trainer[Any],
            prediction_service: PredictionService | None,
            experiment_comparison_service: ExperimentComparisonService | None = None,
    ) -> None:
        self.settings = settings
        self.trainer = trainer
        self.prediction_service = prediction_service
        self.experiment_comparison_service = experiment_comparison_service

    def train(self) -> Any:
        return self.trainer.train()

    def predict(self) -> PredictionOutput:
        if self.prediction_service is None:
            raise RuntimeError("Prediction service is not configured for this application")
        return self.prediction_service.predict()
