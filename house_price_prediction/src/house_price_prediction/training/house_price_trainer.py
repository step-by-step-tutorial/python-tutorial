import logging
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from house_price_prediction.config.settings import AppSettings
from house_price_prediction.dataset.house_dataset import HouseDataset
from house_price_prediction.evaluation.model_evaluator import ModelEvaluator, RegressionMetrics
from house_price_prediction.features.house_feature_model import HouseFeatureModel
from house_price_prediction.features.house_features import HouseFeatureBuilder
from house_price_prediction.model.baseline_model import BaselineModel
from house_price_prediction.model.house_price_model import HousePriceModel
from house_price_prediction.repository.datalake_repository import DataLakeRepository
from house_price_prediction.repository.model_repository import ModelRepository
from house_price_prediction.training.trainer import Trainer
from house_price_prediction.training.training_models import DatasetPartition, DatasetPartitions, TrainingOutput

logger = logging.getLogger(__name__)


class HousePriceTrainer(Trainer[TrainingOutput]):
    def __init__(self, settings: AppSettings, model_repository: ModelRepository) -> None:
        self.settings = settings
        self.repository = DataLakeRepository(settings.data_lake)
        self.model_repository = model_repository

    def train(self) -> TrainingOutput:
        dataset_path = self.download_dataset()
        dataframe = self.prepare_dataset(dataset_path)
        features = self.prepare_features(dataframe)
        target = self.get_target(dataframe)
        dataset_split = self.split_dataset(features, target)

        baseline = self.train_baseline(dataset_split)
        baseline_metrics = self.evaluate_model(baseline, dataset_split, "test")

        model = self.train_model(dataset_split)
        validation_metrics = self.evaluate_model(model, dataset_split, "validation")
        model_metrics = self.evaluate_model(model, dataset_split, "test")
        model_path = self.save_model(model)

        logger.info("House price training completed: model=%s", model_path)
        return TrainingOutput(model_path, baseline_metrics, validation_metrics, model_metrics)

    def download_dataset(self) -> Path:
        dataset_path = self.settings.data_dir / "house.csv"
        self.repository.download_latest_csv(dataset_path)
        return dataset_path

    def prepare_dataset(self, dataset_path: Path) -> pd.DataFrame:
        return HouseDataset(dataset_path).training_frame(self.settings.target_column)

    def prepare_features(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return HouseFeatureBuilder(dataframe, HouseFeatureModel()).build()

    def get_target(self, dataframe: pd.DataFrame) -> pd.Series:
        return dataframe[self.settings.target_column]

    def split_dataset(self, features: pd.DataFrame, target: pd.Series) -> DatasetPartitions:
        train_features, remaining_features, train_target, remaining_target = train_test_split(
            features,
            target,
            test_size=self.settings.validation_size + self.settings.test_size,
            random_state=self.settings.random_state,
        )

        validation_ratio = self.settings.validation_size / (self.settings.validation_size + self.settings.test_size)
        validation_features, test_features, validation_target, test_target = train_test_split(
            remaining_features,
            remaining_target,
            test_size=1 - validation_ratio,
            random_state=self.settings.random_state,
        )

        logger.info(f"Split house dataset: train_rows={len(train_features)} ")
        logger.info(f"validation_rows={len(validation_features)} ")
        logger.info(f"test_rows={len(test_features)}")

        return DatasetPartitions(
            train=DatasetPartition(train_features, train_target),
            validation=DatasetPartition(validation_features, validation_target),
            test=DatasetPartition(test_features, test_target),
        )

    def train_baseline(self, partitions: DatasetPartitions) -> BaselineModel:
        return BaselineModel().fit(partitions.train.features, partitions.train.target)

    def train_model(self, partitions: DatasetPartitions) -> HousePriceModel:
        return HousePriceModel(self.settings.random_state).fit(partitions.train.features, partitions.train.target)

    def evaluate_model(self, model, partitions: DatasetPartitions, dataset_name: str) -> RegressionMetrics:
        dataset = getattr(partitions, dataset_name)
        logger.info("Evaluating model: dataset=%s rows=%s", dataset_name, len(dataset.features))
        return ModelEvaluator(dataset.target, model.predict(dataset.features)).evaluate()

    def save_model(self, model: HousePriceModel) -> Path:
        return self.model_repository.save(model, self.settings.model_dir / "house_price_model.joblib")
