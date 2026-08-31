from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

import pandas as pd

from ml_prediction.data_model.dataset_subset import DatasetSubset
from ml_prediction.data_model.model_metadata import ModelMetadata

TrainingResultType = TypeVar("TrainingResultType")


class Trainer(ABC, Generic[TrainingResultType]):
    @abstractmethod
    def download_dataset(self) -> tuple[pd.DataFrame, Path]:
        ...

    @abstractmethod
    def build_features_and_target(self, dataframe: pd.DataFrame):
        ...

    @abstractmethod
    @abstractmethod
    def train_model(self, partitions):
        ...

    @abstractmethod
    def evaluate_model(self, trained_model, dataset_partition: DatasetSubset):
        ...

    @abstractmethod
    def save_model(self, trained_model, metadata: ModelMetadata) -> Path:
        ...

    @abstractmethod
    def train(self) -> TrainingResultType:
        ...
