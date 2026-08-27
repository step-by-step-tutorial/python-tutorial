import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from house_price_prediction.config.settings import AppSettings
from house_price_prediction.dataset.house_dataset import HouseDataset
from house_price_prediction.evaluation.evaluator import ModelEvaluator, RegressionMetrics
from house_price_prediction.features.house_features import HouseFeatureBuilder
from house_price_prediction.model.baseline_model import BaselineModel
from house_price_prediction.model.house_price_model import HousePriceModel
from house_price_prediction.repository.datalake_repository import DataLakeRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TrainingResult:
    model_path: Path
    baseline_metrics: RegressionMetrics
    validation_metrics: RegressionMetrics
    model_metrics: RegressionMetrics


@dataclass(frozen=True)
class DatasetSplit:
    train_features: pd.DataFrame
    validation_features: pd.DataFrame
    test_features: pd.DataFrame
    train_target: pd.Series
    validation_target: pd.Series
    test_target: pd.Series


class HousePriceTrainer:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.repository = DataLakeRepository(settings.data_lake)
        self.feature_builder = HouseFeatureBuilder()
        self.evaluator = ModelEvaluator()

    def train(self) -> TrainingResult:
        dataset_path = self.download_dataset()
        dataframe = self.prepare_dataset(dataset_path)
        features, target = self.prepare_features_and_target(dataframe)
        dataset_split = self.split_dataset(features, target)

        baseline = self.train_baseline(dataset_split)
        baseline_metrics = self.evaluate_model(baseline, dataset_split, "test")

        model = self.train_model(dataset_split)
        validation_metrics = self.evaluate_model(model, dataset_split, "validation")
        model_metrics = self.evaluate_model(model, dataset_split, "test")
        model_path = self.save_model(model)

        logger.info("House price training completed: model=%s", model_path)
        return TrainingResult(model_path, baseline_metrics, validation_metrics, model_metrics)

    def download_dataset(self) -> Path:
        dataset_path = self.settings.data_dir / "house.csv"
        self.repository.download_latest_csv(dataset_path)
        return dataset_path

    def prepare_dataset(self, dataset_path: Path) -> pd.DataFrame:
        return HouseDataset(dataset_path).training_frame(self.settings.target_column)

    def prepare_features_and_target(
            self,
            dataframe: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.Series]:
        features = self.feature_builder.build(dataframe)
        target = dataframe[self.settings.target_column]
        return features, target

    def split_dataset(self, features: pd.DataFrame, target: pd.Series) -> DatasetSplit:
        train_features, remaining_features, train_target, remaining_target = train_test_split(
            features,
            target,
            test_size=self.settings.validation_size + self.settings.test_size,
            random_state=self.settings.random_state,
        )
        validation_ratio = self.settings.validation_size / (
            self.settings.validation_size + self.settings.test_size
        )
        validation_features, test_features, validation_target, test_target = train_test_split(
            remaining_features,
            remaining_target,
            test_size=1 - validation_ratio,
            random_state=self.settings.random_state,
        )
        logger.info(
            "Split house dataset: train_rows=%s validation_rows=%s test_rows=%s",
            len(train_features),
            len(validation_features),
            len(test_features),
        )
        return DatasetSplit(
            train_features,
            validation_features,
            test_features,
            train_target,
            validation_target,
            test_target,
        )

    def train_baseline(self, dataset_split: DatasetSplit) -> BaselineModel:
        return BaselineModel().fit(dataset_split.train_features, dataset_split.train_target)

    def train_model(self, dataset_split: DatasetSplit) -> HousePriceModel:
        return HousePriceModel(self.settings.random_state).fit(
            dataset_split.train_features,
            dataset_split.train_target,
        )

    def evaluate_model(
            self,
            model,
            dataset_split: DatasetSplit,
            dataset_name: str,
    ) -> RegressionMetrics:
        features = getattr(dataset_split, f"{dataset_name}_features")
        target = getattr(dataset_split, f"{dataset_name}_target")
        logger.info("Evaluating model: dataset=%s rows=%s", dataset_name, len(features))
        return self.evaluator.evaluate(target, model.predict(features))

    def save_model(self, model: HousePriceModel) -> Path:
        return model.save(self.settings.model_dir / "house_price_model.joblib")
