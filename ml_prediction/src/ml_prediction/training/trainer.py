from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

import pandas as pd

from ml_prediction.data_model.features_and_target import FeaturesAndTarget
from ml_prediction.offline_tracking.models import ModelMetadata

TrainingResultType = TypeVar("TrainingResultType")


class Trainer(ABC, Generic[TrainingResultType]):
    @abstractmethod
    def download_dataset(self) -> tuple[pd.DataFrame, Path]:
        ...

    @abstractmethod
    def build_features_and_target(self, dataframe: pd.DataFrame):
        ...

    @abstractmethod
    def train_model(self, partitions):
        ...

    @abstractmethod
    def evaluate_model(self, model, data: FeaturesAndTarget):
        ...

    @abstractmethod
    def save_model(self, model, metadata: ModelMetadata) -> Path:
        ...

    @abstractmethod
    def train(self) -> TrainingResultType:
        ...
