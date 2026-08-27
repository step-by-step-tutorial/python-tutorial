from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

from ml_prediction.training.training_models import DatasetPartition

TrainingResultType = TypeVar("TrainingResultType")


class Trainer(ABC, Generic[TrainingResultType]):
    @abstractmethod
    def download_dataset(self) -> Path:
        ...

    @abstractmethod
    def prepare_dataset(self, dataset_path: Path):
        ...

    @abstractmethod
    def build_features(self, dataframe):
        ...

    @abstractmethod
    def get_target(self, dataframe):
        ...

    @abstractmethod
    def split_dataset(self, features, target):
        ...

    @abstractmethod
    def train_baseline(self, partitions):
        ...

    @abstractmethod
    def train_model(self, partitions):
        ...

    @abstractmethod
    def evaluate_model(self, model, dataset: DatasetPartition):
        ...

    @abstractmethod
    def save_model(self, model) -> Path:
        ...

    @abstractmethod
    def train(self) -> TrainingResultType:
        ...
