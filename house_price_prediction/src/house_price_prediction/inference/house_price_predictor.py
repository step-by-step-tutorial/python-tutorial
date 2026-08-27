import logging
from pathlib import Path

import pandas as pd

from house_price_prediction.features.house_features import HouseFeatureBuilder
from house_price_prediction.model.house_price_model import HousePriceModel
from house_price_prediction.inference.predictor import Predictor

logger = logging.getLogger(__name__)


class HousePricePredictor(Predictor[pd.Series]):
    def __init__(self, model_path: Path) -> None:
        self.model = HousePriceModel.load(model_path)
        self.feature_builder = HouseFeatureBuilder()

    def predict(self, dataframe: pd.DataFrame) -> pd.Series:
        features = self.feature_builder.build(dataframe)
        predictions = self.model.predict(features)
        logger.info(f"Generated house price predictions: rows={len(predictions)}")
        return pd.Series(predictions, index=dataframe.index, name="predicted_total_price")
