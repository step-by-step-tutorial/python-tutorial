import logging
from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd

from ml_prediction.dataset.dataset import Dataset
from ml_prediction.features.feature_builder import FeatureBuilder
from ml_prediction.utils.csv_utils import load_csv

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PreparedTrainingData:
    features: pd.DataFrame
    target: pd.Series


class TabularDataset(Dataset):
    def training_frame(self, target_column: str) -> pd.DataFrame:
        dataframe = load_csv(self.path).copy()
        dataframe = dataframe.dropna(subset=[target_column])
        logger.info(f"Prepared training frame: rows={len(dataframe)} target={target_column}")
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
            f"Prepared training data: rows={len(dataframe)} features={len(features.columns)} target={target_column}"
        )
        return PreparedTrainingData(features, target)
