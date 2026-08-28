import logging
from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd

from ml_prediction.dataset.dataset import Dataset
from ml_prediction.features.feature_builder import FeatureBuilder

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PreparedTrainingData:
    features: pd.DataFrame
    target: pd.Series


class HouseDataset(Dataset):
    def load(self) -> pd.DataFrame:
        logger.info(f"Loading house dataset: path={self.path}")
        dataframe = pd.read_csv(self.path)
        logger.info(f"House dataset loaded: rows={len(dataframe)} columns={len(dataframe.columns)}")
        return dataframe

    def training_frame(self, target_column: str) -> pd.DataFrame:
        dataframe = self.load().copy()
        if target_column not in dataframe.columns:
            raise ValueError(f"Target column '{target_column}' is missing from the dataset")
        dataframe[target_column] = pd.to_numeric(dataframe[target_column], errors="coerce")
        dataframe = dataframe.dropna(subset=[target_column])
        logger.info("Prepared training frame: rows=%s target=%s", len(dataframe), target_column)
        return dataframe

    def prepare_training_data(
            self,
            target_column: str,
            feature_builder_factory: Callable[[pd.DataFrame], FeatureBuilder],
    ) -> PreparedTrainingData:
        dataframe = self.training_frame(target_column)
        target = dataframe.pop(target_column)
        features = feature_builder_factory(dataframe).build()
        logger.info(
            "Prepared training data: rows=%s features=%s target=%s",
            len(features),
            len(features.columns),
            target_column,
        )
        return PreparedTrainingData(features, target)
