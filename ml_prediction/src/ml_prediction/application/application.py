from typing import Any

from ml_prediction.config.settings import AppSettings
from ml_prediction.inference.prediction_service import PredictionOutput
from ml_prediction.inference.prediction_service import PredictionService
from ml_prediction.training.trainer import Trainer


class Application:
    def __init__(
            self,
            settings: AppSettings,
            trainer: Trainer[Any],
            prediction_service: PredictionService,
    ) -> None:
        self.settings = settings
        self.trainer = trainer
        self.prediction_service = prediction_service

    def train(self) -> Any:
        return self.trainer.train()

    def predict(self) -> PredictionOutput:
        return self.prediction_service.predict()
