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
    def train_baseline(self, partitions):
        ...

    @abstractmethod
    def train_model(self, partitions):
        ...

    @abstractmethod
    def evaluate_model(self, trained_model, dataset_partition: DatasetPartition):
        ...

    @abstractmethod
    def save_model(self, trained_model) -> Path:
        ...

    @abstractmethod
    def train(self) -> TrainingResultType:
        ...
