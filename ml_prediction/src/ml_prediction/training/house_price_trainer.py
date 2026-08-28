import logging
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from ml_prediction.config.settings import AppSettings, DatasetSource
from ml_prediction.dataset.house_dataset import HouseDataset, PreparedTrainingData
from ml_prediction.evaluation.model_evaluator import ModelEvaluator, RegressionMetrics
from ml_prediction.features.house_feature_model import HouseFeatureModel
from ml_prediction.features.house_features import HouseFeatureBuilder
from ml_prediction.model.baseline_model import BaselineModel
from ml_prediction.model.house_price_model import HousePriceModel
from ml_prediction.pipeline.house_price_pipeline_builder import HousePricePipelineBuilder
from ml_prediction.repository.datalake_repository import DataLakeRepository
from ml_prediction.repository.local_model_repository import LocalModelRepository
from ml_prediction.reporting.report_service import ReportService
from ml_prediction.training.trainer import Trainer
from ml_prediction.training.training_models import DatasetPartition, DatasetPartitions, TrainingOutput

logger = logging.getLogger(__name__)


class HousePriceTrainer(Trainer[TrainingOutput]):
    def __init__(
            self,
            settings: AppSettings,
            data_lake_repository: DataLakeRepository,
            model_repository: LocalModelRepository,
            report_service: ReportService | None = None,
    ) -> None:
        self.settings = settings
        self.report_service = report_service or ReportService(settings.report_dir)
        self.data_lake_repository = data_lake_repository
        self.model_repository = model_repository
        self.feature_model = HouseFeatureModel()
        self.pipeline_builder = HousePricePipelineBuilder(
            self.feature_model,
            settings.model_type,
            settings.n_estimators,
            settings.n_jobs,
            settings.random_state,
        )

    def train(self) -> TrainingOutput:
        model_path = self.settings.model_dir / "house_price_model.joblib"
        report = self.report_service.start("house", "training", model_path)
        dataset_path = self.download_dataset()
        report.record("dataset_downloaded", details=str(dataset_path))
        prepared_data = self.prepare_dataset(dataset_path)
        report.record("dataset_prepared", rows=len(prepared_data.features), details=f"target={self.settings.target_column}")
        report.record("features_built", rows=len(prepared_data.features), details=f"columns={len(prepared_data.features.columns)}")
        report.record("target_extracted", rows=len(prepared_data.target), details=f"column={self.settings.target_column}")
        dataset_split = self.split_dataset(prepared_data.features, prepared_data.target)
        report.record(
            "dataset_split",
            rows=len(prepared_data.features),
            details=(
                f"train={len(dataset_split.train.features)} "
                f"validation={len(dataset_split.validation.features)} "
                f"test={len(dataset_split.test.features)}"
            ),
        )

        baseline = self.train_baseline(dataset_split)
        report.record("baseline_trained", partition="train", rows=len(dataset_split.train.features), model="baseline")
        logger.info("Evaluating model: model=baseline partition=test rows=%s", len(dataset_split.test.features))
        baseline_metrics = self.evaluate_model(baseline, dataset_split.test)
        report.record(
            "model_evaluated",
            partition="test",
            rows=len(dataset_split.test.features),
            model="baseline",
            metrics=baseline_metrics,
        )

        model = self.train_model(dataset_split)
        report.record("model_trained", partition="train", rows=len(dataset_split.train.features), model="house_price")
        logger.info(
            "Evaluating model: model=house_price partition=validation rows=%s",
            len(dataset_split.validation.features),
        )
        validation_metrics = self.evaluate_model(model, dataset_split.validation)
        report.record(
            "model_evaluated",
            partition="validation",
            rows=len(dataset_split.validation.features),
            model="house_price",
            metrics=validation_metrics,
        )
        logger.info("Evaluating model: model=house_price partition=test rows=%s", len(dataset_split.test.features))
        model_metrics = self.evaluate_model(model, dataset_split.test)
        report.record(
            "model_evaluated",
            partition="test",
            rows=len(dataset_split.test.features),
            model="house_price",
            metrics=model_metrics,
        )
        model_path = self.save_model(model)
        report.record("model_saved", model_path=model_path, details=str(model_path))
        report.record("training_completed", details=str(report.path))

        logger.info("House price training completed: model=%s", model_path)
        return TrainingOutput(model_path, baseline_metrics, validation_metrics, model_metrics, report.path)

    def download_dataset(self) -> Path:
        dataset_path = self.settings.data_dir / "house.csv"
        if self.settings.dataset_source == DatasetSource.DOWNLOAD:
            self.data_lake_repository.download_latest_csv(dataset_path)
        else:
            logger.info("Using local dataset: path=%s", dataset_path)
        return dataset_path

    def prepare_dataset(self, dataset_path: Path) -> PreparedTrainingData:
        return HouseDataset(dataset_path).prepare_training_data(
            self.settings.target_column,
            lambda dataframe: HouseFeatureBuilder(dataframe, self.feature_model),
        )

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

        logger.info(f"Split house dataset: train_rows={len(train_features)} "
                    f"validation_rows={len(validation_features)}"
                    f"test_rows={len(test_features)}")

        return DatasetPartitions(
            train=DatasetPartition(train_features, train_target),
            validation=DatasetPartition(validation_features, validation_target),
            test=DatasetPartition(test_features, test_target),
        )

    def train_baseline(self, partitions: DatasetPartitions) -> BaselineModel:
        return BaselineModel().fit(partitions.train.features, partitions.train.target)

    def train_model(self, partitions: DatasetPartitions) -> HousePriceModel:
        return HousePriceModel(self.pipeline_builder).fit(partitions.train.features, partitions.train.target)

    def evaluate_model(self, model, dataset: DatasetPartition) -> RegressionMetrics:
        return ModelEvaluator(dataset.target, model.predict(dataset.features)).evaluate()

    def save_model(self, model: HousePriceModel) -> Path:
        return self.model_repository.save(model, self.settings.model_dir / "house_price_model.joblib")
