from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

import pandas as pd

from ml_prediction.audit.data.metadata import Metadata
from ml_prediction.data_model.classification_evaluation_data import ClassificationEvaluationData
from ml_prediction.data_model.evaluation_data import RegressionEvaluationData
from ml_prediction.data_model.features_and_target import FeaturesAndTarget

TrainingResultType = TypeVar("TrainingResultType")
EvaluationType = RegressionEvaluationData | ClassificationEvaluationData


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
    def save_model(self, model, metadata: Metadata) -> Path:
        ...

    @abstractmethod
    def train(self) -> TrainingResultType:
        ...
