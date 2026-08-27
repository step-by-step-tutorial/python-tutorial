from abc import ABC, abstractmethod
from typing import Generic, TypeVar

import pandas as pd

PredictionType = TypeVar("PredictionType")


class Predictor(ABC, Generic[PredictionType]):
    @abstractmethod
    def predict(self, dataframe: pd.DataFrame) -> PredictionType:
        ...
