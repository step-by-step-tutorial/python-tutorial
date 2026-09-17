from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

import pandas as pd

PredictionType = TypeVar("PredictionType")


class Predictor(ABC, Generic[PredictionType]):
    @property
    def model_path(self) -> Path | None:
        return None

    @property
    @abstractmethod
    def prediction_column(self) -> str:
        ...

    @abstractmethod
    def predict(self, dataframe: pd.DataFrame) -> PredictionType:
        ...
