import logging
from pathlib import Path

import pandas as pd

from house_price_prediction.features.house_feature_model import HouseFeatureModel
from house_price_prediction.features.house_features import HouseFeatureBuilder
from house_price_prediction.inference.predictor import Predictor
from house_price_prediction.repository.local_repository import LocalRepository

logger = logging.getLogger(__name__)


class HousePricePredictor(Predictor[pd.Series]):
    def __init__(self, model_path: Path, model_repository: LocalRepository) -> None:
        self.model = model_repository.load(model_path)

    def predict(self, dataframe: pd.DataFrame) -> pd.Series:
        features = HouseFeatureBuilder(dataframe, HouseFeatureModel()).build()
        predictions = self.model.predict(features)
        logger.info(f"Generated house price predictions: rows={len(predictions)}")
        return pd.Series(predictions, index=dataframe.index, name="predicted_total_price")
