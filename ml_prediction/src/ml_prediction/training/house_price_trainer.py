import logging
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ml_prediction.config.settings import AppSettings, DatasetSource
from ml_prediction.dataset.house_dataset import HouseDataset, PreparedTrainingData
from ml_prediction.evaluation.model_evaluator import ModelEvaluator, RegressionMetrics
from ml_prediction.features.feature_builder import FeatureBuilder
from ml_prediction.features.house_feature_model import HouseFeatureModel
from ml_prediction.model.baseline_model import BaselineModel
from ml_prediction.model.house_price_model import HousePriceModel
from ml_prediction.model.model_metadata import ModelMetadata
from ml_prediction.pipeline.pipeline_builder import PipelineBuilder
from ml_prediction.repository.datalake_repository import DataLakeRepository
from ml_prediction.repository.local_model_repository import LocalModelRepository
from ml_prediction.reporting.report_service import ReportService
from ml_prediction.training.trainer import Trainer
from ml_prediction.training.dataset_splitter import DatasetSplitter
from ml_prediction.training.training_models import DatasetPartition, DatasetPartitions, TrainingOutput

logger = logging.getLogger(__name__)


class HousePriceTrainer(Trainer[TrainingOutput]):
    def __init__(
            self,
            settings: AppSettings,
            dataset: HouseDataset,
            feature_model: HouseFeatureModel,
            feature_builder_factory: Callable[[pd.DataFrame], FeatureBuilder],
            data_lake_repository: DataLakeRepository,
            model_repository: LocalModelRepository,
            pipeline_builder: PipelineBuilder,
            evaluator: ModelEvaluator,
            dataset_splitter: DatasetSplitter,
            report_service: ReportService | None = None,
    ) -> None:
        self.settings = settings
        self.dataset = dataset
        self.feature_model = feature_model
        self.feature_builder_factory = feature_builder_factory
        self.report_service = report_service or ReportService(settings.report_dir)
        self.data_lake_repository = data_lake_repository
        self.model_repository = model_repository
        self.pipeline_builder = pipeline_builder
        self.evaluator = evaluator
        self.dataset_splitter = dataset_splitter

    def train(self) -> TrainingOutput:
        model_path = self.settings.model_dir / "house_price_model.joblib"
        report = self.report_service.start("house", "training", model_path)
        dataset_path = self.download_dataset()
        report.record("dataset_downloaded", details=str(dataset_path))
        prepared_data = self.prepare_dataset(dataset_path)
        report.record("dataset_prepared", rows=len(prepared_data.features), details=f"target={self.settings.target_column}")
        report.record("features_built", rows=len(prepared_data.features), details=f"columns={len(prepared_data.features.columns)}")
        report.record("target_extracted", rows=len(prepared_data.target), details=f"column={self.settings.target_column}")
        dataset_split = self.dataset_splitter.split(prepared_data.features, prepared_data.target)
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
        # Validation is the intermediate set for comparing the baseline and trained model.
        logger.info(
            "Evaluating model: model=baseline partition=validation rows=%s",
            len(dataset_split.validation.features),
        )
        baseline_validation_metrics = self.evaluate_model(baseline, dataset_split.validation)
        report.record(
            "model_evaluated",
            partition="validation",
            rows=len(dataset_split.validation.features),
            model="baseline",
            metrics=baseline_validation_metrics,
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
        # Test is held back until this final evaluation and does not guide selection.
        final_test_metrics = self.evaluate_model(model, dataset_split.test)
        report.record(
            "model_evaluated",
            partition="test",
            rows=len(dataset_split.test.features),
            model="house_price",
            metrics=final_test_metrics,
        )
        metadata = ModelMetadata(
            model_type=self.settings.model_type,
            model_parameters={
                "n_estimators": self.settings.n_estimators,
                "n_jobs": self.settings.n_jobs,
                "random_state": self.settings.random_state,
            },
            target_column=self.settings.target_column,
            numeric_features=self.feature_model.get_numeric_features(),
            boolean_features=self.feature_model.get_boolean_features(),
            categorical_features=self.feature_model.get_categorical_features(),
            training_timestamp=datetime.now(timezone.utc),
            validation_metrics=validation_metrics,
            final_test_metrics=final_test_metrics,
            schema_version="1",
            model_version="1",
        )
        model_path = self.save_model(model, metadata)
        report.record("model_saved", model_path=model_path, details=str(model_path))
        report.record("training_completed", details=str(report.path))

        logger.info("House price training completed: model=%s", model_path)
        return TrainingOutput(
            model_path,
            baseline_validation_metrics,
            validation_metrics,
            final_test_metrics,
            report.path,
        )

    def download_dataset(self) -> Path:
        dataset_path = self.settings.data_dir / "house.csv"
        if self.settings.dataset_source == DatasetSource.DOWNLOAD:
            self.data_lake_repository.download_latest_csv(dataset_path)
        else:
            logger.info("Using local dataset: path=%s", dataset_path)
        return dataset_path

    def prepare_dataset(self, dataset_path: Path) -> PreparedTrainingData:
        if self.dataset.path != dataset_path:
            raise ValueError(f"Dataset path does not match configured path: {self.dataset.path}")
        return self.dataset.prepare_training_data(
            self.settings.target_column,
            self.feature_builder_factory,
        )

    def train_baseline(self, partitions: DatasetPartitions) -> BaselineModel:
        # The baseline is a validation-only comparator and is never persisted or inferred with.
        return BaselineModel().fit(partitions.train.features, partitions.train.target)

    def train_model(self, partitions: DatasetPartitions) -> HousePriceModel:
        return HousePriceModel(self.pipeline_builder).fit(partitions.train.features, partitions.train.target)

    def evaluate_model(self, model, dataset: DatasetPartition) -> RegressionMetrics:
        return self.evaluator.evaluate(dataset.target, model.predict(dataset.features))

    def save_model(self, model: HousePriceModel, metadata: ModelMetadata) -> Path:
        return self.model_repository.save(
            model,
            self.settings.model_dir / "house_price_model.joblib",
            metadata,
        )
