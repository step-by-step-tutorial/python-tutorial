from abc import ABC, abstractmethod

import pandas as pd

from house_price_prediction.features.feature_model import FeatureModel


class FeatureBuilder(ABC):
    def __init__(self, dataframe: pd.DataFrame, feature_model: FeatureModel) -> None:
        self._dataframe = dataframe
        self._feature_model = feature_model

    @abstractmethod
    def build(self) -> pd.DataFrame:
        raise NotImplementedError
