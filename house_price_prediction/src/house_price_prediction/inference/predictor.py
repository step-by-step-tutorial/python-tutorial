import logging
from pathlib import Path

import pandas as pd

from house_price_prediction.features.house_features import HouseFeatureBuilder
from house_price_prediction.model.house_price_model import HousePriceModel

logger = logging.getLogger(__name__)


class HousePricePredictor:
    def __init__(self, model_path: Path) -> None:
        self.model = HousePriceModel.load(model_path)
        self.feature_builder = HouseFeatureBuilder()

    def predict(self, dataframe: pd.DataFrame) -> pd.Series:
        features = self.feature_builder.build(dataframe)
        predictions = self.model.predict(features)
        logger.info("Generated house price predictions: rows=%s", len(predictions))
        return pd.Series(predictions, index=dataframe.index, name="predicted_total_price")
