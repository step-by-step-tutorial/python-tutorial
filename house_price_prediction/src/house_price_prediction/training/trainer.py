from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar


TrainingResultType = TypeVar("TrainingResultType")


class Trainer(ABC, Generic[TrainingResultType]):
    @abstractmethod
    def download_dataset(self) -> Path:
        ...

    @abstractmethod
    def prepare_dataset(self, dataset_path: Path):
        ...

    @abstractmethod
    def prepare_features_and_target(self, dataframe):
        ...

    @abstractmethod
    def split_dataset(self, features, target):
        ...

    @abstractmethod
    def train_baseline(self, dataset_split):
        ...

    @abstractmethod
    def train_model(self, dataset_split):
        ...

    @abstractmethod
    def evaluate_model(self, model, dataset_split, dataset_name: str):
        ...

    @abstractmethod
    def save_model(self, model) -> Path:
        ...

    @abstractmethod
    def train(self) -> TrainingResultType:
        ...
