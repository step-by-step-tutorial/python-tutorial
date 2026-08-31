import logging
from pathlib import Path

import pandas as pd

from ml_prediction.config.settings import get_settings
from ml_prediction.features.feature_builder import FeatureBuilder
from ml_prediction.features.feature_model import FeatureModel
from ml_prediction.inference.predictor import Predictor
from ml_prediction.repository.local_model_repository import LocalModelRepository

logger = logging.getLogger(__name__)


class ModelPredictor(Predictor[pd.Series]):

    def __init__(
            self,
            dataset_name: str,
            feature_model: FeatureModel,
    ) -> None:
        self._settings = get_settings(dataset_name)
        self._model_path = self._settings.model_dir / self._settings.model_filename
        self._model = LocalModelRepository().load(self._model_path)
        self._feature_model = feature_model

    @property
    def model_path(self) -> Path:
        return self._model_path

    @property
    def prediction_column(self) -> str:
        return self._settings.prediction_column

    def predict(self, dataframe: pd.DataFrame) -> pd.Series:
        features = FeatureBuilder(dataframe, self._feature_model).build()
        predictions = self._model.predict(features)
        logger.info(f"Generated predictions: rows={len(predictions)} prediction_column={self.prediction_column}")
        return pd.Series(predictions, index=dataframe.index, name=self.prediction_column)
