from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

import pandas as pd

PredictionType = TypeVar("PredictionType")


class Predictor(ABC, Generic[PredictionType]):
    @property
    @abstractmethod
    def model_path(self) -> Path:
        ...

    @property
    @abstractmethod
    def prediction_column(self) -> str:
        ...

    @abstractmethod
    def predict(self, dataframe: pd.DataFrame) -> PredictionType:
        ...
