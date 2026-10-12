import logging

import pandas as pd

from ml_prediction.audit.audit_service import AuditService
from ml_prediction.config.operation import Operation
from ml_prediction.model.prediction_model import PredictionModel
from ml_prediction.model.settings_model import SettingsModel
from ml_prediction.repository.dataset_repository import DatasetRepository
from ml_prediction.repository.model_repository import ModelRepository
from ml_prediction.repository.prediction_repository import PredictionRepository

logger = logging.getLogger(__name__)


class Predictor:
    def __init__(self, settings: SettingsModel) -> None:
        self._settings = settings
        self._audit = AuditService(settings, Operation.PREDICT)
        self._dataset_repository = DatasetRepository(settings)
        self._model_repository = ModelRepository()
        self._prediction_repository = PredictionRepository()

    def predict(self) -> PredictionModel:
        settings = self._settings
        profile = settings.profile
        logger.info("Prediction started: dataset=%s run_id=%s", settings.dataset_name, self._audit.run_id)

        pipeline = self._model_repository.load(settings.model_path)
        self._audit.log_step("model_loaded", model_path=settings.model_path)

        dataframe, dataset_path = self._dataset_repository.load()
        self._audit.log_step("dataset_loaded", rows=len(dataframe), details=str(dataset_path))

        features = profile.features.extract(dataframe)
        predictions = pd.Series(pipeline.predict(features), index=dataframe.index, name=profile.prediction_column)
        self._audit.log_step("predictions_generated", rows=len(predictions),
                             details=f"columns={len(features.columns)}")

        prediction = PredictionModel(dataframe, predictions, dataset_path, profile.prediction_column,
                                     settings.task_type)
        output_path = self._prediction_repository.save(settings.prediction_path, prediction)
        self._audit.log_step("prediction_saved", rows=len(predictions), details=str(output_path))
        return prediction
