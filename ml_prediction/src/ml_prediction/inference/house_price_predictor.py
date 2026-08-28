import logging
from collections.abc import Callable
from pathlib import Path

import pandas as pd

from ml_prediction.features.house_features import HouseFeatureBuilder
from ml_prediction.inference.predictor import Predictor
from ml_prediction.repository.local_model_repository import LocalModelRepository

logger = logging.getLogger(__name__)


class HousePricePredictor(Predictor[pd.Series]):
    def __init__(
            self,
            model_path: Path,
            model_repository: LocalModelRepository,
            feature_builder_factory: Callable[[pd.DataFrame], HouseFeatureBuilder],
    ) -> None:
        self._model_path = model_path
        self._feature_builder_factory = feature_builder_factory
        self.model = model_repository.load(model_path)

    @property
    def model_path(self) -> Path:
        return self._model_path

    def predict(self, dataframe: pd.DataFrame) -> pd.Series:
        features = self._feature_builder_factory(dataframe).build()
        predictions = self.model.predict(features)
        logger.info(f"Generated house price predictions: rows={len(predictions)}")
        return pd.Series(predictions, index=dataframe.index, name="predicted_total_price")
