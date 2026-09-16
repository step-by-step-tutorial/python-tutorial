from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

import pandas as pd

from ml_prediction.audit.model_metadata import ModelMetadata
from ml_prediction.data_model.classification_evaluation import ClassificationEvaluation
from ml_prediction.data_model.evaluation import RegressionEvaluation
from ml_prediction.data_model.features_and_target import FeaturesAndTarget

TrainingResultType = TypeVar("TrainingResultType")
EvaluationType = RegressionEvaluation | ClassificationEvaluation


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
    def evaluate_model_with_predictions(self, model, data: FeaturesAndTarget) -> EvaluationType:
        ...

    @abstractmethod
    def save_model(self, model, metadata: ModelMetadata) -> Path:
        ...

    @abstractmethod
    def train(self) -> TrainingResultType:
        ...
