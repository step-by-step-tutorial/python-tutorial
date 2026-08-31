import logging
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd

from ml_prediction.config.settings import DatasetSource, TaskType
from ml_prediction.data_model.dataset_partition import DatasetPartition
from ml_prediction.data_model.dataset_partitions import DatasetPartitions
from ml_prediction.data_model.evaluation_result import Evaluation
from ml_prediction.evaluation.model_evaluator import ModelEvaluator
from ml_prediction.data_model.experiment_result import Experiment
from ml_prediction.data_model.model_metadata import (
    CURRENT_MODEL_VERSION,
    CURRENT_SCHEMA_VERSION,
    ModelMetadata,
)
from ml_prediction.data_model.app_settings import AppSettings
from ml_prediction.data_model.prepared_training_data import PreparedTrainingData
from ml_prediction.data_model.regression_metrics import RegressionMetrics
from ml_prediction.dataset.house_dataset import HouseDataset
from ml_prediction.features.feature_builder import FeatureBuilder
from ml_prediction.features.house_feature_model import HouseFeatureModel
from ml_prediction.model.baseline_model import BaselineModel
from ml_prediction.model.house_price_model import HousePriceModel
from ml_prediction.pipeline.pipeline_builder import PipelineBuilder
from ml_prediction.reporting.experiment_repository import ExperimentRepository
from ml_prediction.reporting.report_service import ReportService
from ml_prediction.repository.datalake_repository import DataLakeRepository
from ml_prediction.repository.local_model_repository import LocalModelRepository
from ml_prediction.training.dataset_splitter import DatasetSplitter
from ml_prediction.training.trainer import Trainer
from ml_prediction.visualization.experiment_visualizer import ExperimentVisualizer
from ml_prediction.visualization.training_visualizer import TrainingVisualizer

logger = logging.getLogger(__name__)


class HousePriceTrainer(Trainer[Experiment]):
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
            report_service: ReportService,
            experiment_repository: ExperimentRepository,
            training_visualizer: TrainingVisualizer,
            experiment_visualizer: ExperimentVisualizer,
    ) -> None:
        self.settings = settings
        self.dataset = dataset
        self.feature_model = feature_model
        self.feature_builder_factory = feature_builder_factory
        self.report_service = report_service
        self.experiment_repository = experiment_repository
        self.training_visualizer = training_visualizer
        self.experiment_visualizer = experiment_visualizer
        self.data_lake_repository = data_lake_repository
        self.model_repository = model_repository
        self.pipeline_builder = pipeline_builder
        self.evaluator = evaluator
        self.dataset_splitter = dataset_splitter

    def train(self) -> Experiment:
        if self.settings.task_type != TaskType.REGRESSION:
            raise ValueError(
                f"HousePriceTrainer supports only regression tasks, got '{self.settings.task_type}'"
            )
        report_events: list[tuple[str, dict[str, object]]] = []

        def record_report(step: str, **details: object) -> None:
            report_events.append((step, details))

        model_path = self.settings.model_dir / self.settings.model_filename
        dataset_path = self.download_dataset()
        prepared_training_data = self.prepare_dataset(dataset_path)
        record_report("dataset_downloaded", details=str(dataset_path))
        record_report(
            "dataset_prepared",
            rows=len(prepared_training_data.features),
            details=f"target={self.settings.target_column}",
        )
        record_report(
            "features_built",
            rows=len(prepared_training_data.features),
            details=f"columns={len(prepared_training_data.features.columns)}",
        )
        record_report(
            "target_extracted",
            rows=len(prepared_training_data.target),
            details=f"column={self.settings.target_column}",
        )
        dataset_partitions = self.dataset_splitter.split(
            prepared_training_data.features,
            prepared_training_data.target,
        )
        record_report(
            "dataset_split",
            rows=len(prepared_training_data.features),
            details=(
                f"train={len(dataset_partitions.train.features)} "
                f"validation={len(dataset_partitions.validation.features)} "
                f"test={len(dataset_partitions.test.features)}"
            ),
        )

        experiment_id = str(uuid4())
        experiment_timestamp = datetime.now(timezone.utc)
        model_parameters = {
            "n_estimators": self.settings.n_estimators,
            "n_jobs": self.settings.n_jobs,
            "max_depth": self.settings.max_depth,
            "min_samples_split": self.settings.min_samples_split,
            "min_samples_leaf": self.settings.min_samples_leaf,
            "max_features": self.settings.max_features,
            "bootstrap": self.settings.bootstrap,
            "random_state": self.settings.random_state,
        }
        logger.info(
            "Starting training experiment: experiment_id=%s model_type=%s model_parameters=%s",
            experiment_id,
            self.settings.model_type,
            model_parameters,
        )

        baseline_model = self.train_baseline(dataset_partitions)
        record_report(
            "baseline_trained",
            partition="train",
            rows=len(dataset_partitions.train.features),
            model_name="baseline",
        )
        # Validation is the intermediate set for comparing the baseline and trained model.
        logger.info(
            "Evaluating model: model=baseline partition=validation rows=%s",
            len(dataset_partitions.validation.features),
        )
        baseline_validation_metrics = self.evaluate_model(baseline_model, dataset_partitions.validation)
        record_report(
            "model_evaluated",
            partition="validation",
            rows=len(dataset_partitions.validation.features),
            model_name="baseline",
            metrics=baseline_validation_metrics,
        )

        trained_model = self.train_model(dataset_partitions)
        record_report(
            "model_trained",
            partition="train",
            rows=len(dataset_partitions.train.features),
            model_name=self.settings.model_type,
        )
        logger.info(
            "Evaluating model: model=%s partition=validation rows=%s",
            self.settings.model_type,
            len(dataset_partitions.validation.features),
        )
        validation_metrics = self.evaluate_model(trained_model, dataset_partitions.validation)
        record_report(
            "model_evaluated",
            partition="validation",
            rows=len(dataset_partitions.validation.features),
            model_name=self.settings.model_type,
            metrics=validation_metrics,
        )
        logger.info(
            "Evaluating model: model=%s partition=test rows=%s",
            self.settings.model_type,
            len(dataset_partitions.test.features),
        )
        # Test is held back until this final evaluation and does not guide selection.
        final_test_evaluation = self.evaluate_model_with_predictions(
            trained_model,
            dataset_partitions.test,
        )
        final_test_metrics = final_test_evaluation.metrics
        record_report(
            "model_evaluated",
            partition="test",
            rows=len(dataset_partitions.test.features),
            model_name=self.settings.model_type,
            metrics=final_test_metrics,
        )
        model_parameters = self._fitted_model_parameters(trained_model, model_parameters)
        metadata = ModelMetadata(
            model_type=self.settings.model_type,
            model_parameters=model_parameters,
            target_column=self.settings.target_column,
            numeric_features=self.feature_model.get_numeric_features(),
            boolean_features=self.feature_model.get_boolean_features(),
            categorical_features=self.feature_model.get_categorical_features(),
            training_timestamp=experiment_timestamp,
            validation_metrics=validation_metrics,
            final_test_metrics=final_test_metrics,
            schema_version=CURRENT_SCHEMA_VERSION,
            model_version=CURRENT_MODEL_VERSION,
            dataset_name=self.settings.dataset_name,
            task_type=self.settings.task_type.value,
            prediction_column=self.settings.prediction_column,
        )
        model_path = self.save_model(trained_model, metadata)
        report = self.report_service.start(self.settings.dataset_name, "training", model_path)
        for step, details in report_events:
            report.record(step, **details)
        report.record("model_saved", model_path=model_path, details=str(model_path))
        report.record("training_completed", details=str(report.path))

        result = Experiment(
            experiment_id=experiment_id,
            timestamp=experiment_timestamp,
            dataset_name=self.settings.dataset_name,
            model_type=self.settings.model_type,
            model_parameters=metadata.model_parameters,
            baseline_validation_metrics=baseline_validation_metrics,
            validation_metrics=validation_metrics,
            test_metrics=final_test_metrics,
            model_path=model_path,
            report_path=report.path,
        )
        self.experiment_repository.save(result)
        self.training_visualizer.save_actual_vs_predicted(
            final_test_evaluation.y_true,
            final_test_evaluation.y_pred,
            experiment_id,
            self.settings.report_dir,
        )
        self.training_visualizer.save_residual_vs_predicted(
            final_test_evaluation.y_true,
            final_test_evaluation.y_pred,
            experiment_id,
            self.settings.report_dir,
        )
        self.training_visualizer.save_feature_importance(
            trained_model,
            experiment_id,
            self.settings.report_dir,
        )
        self.experiment_visualizer.save_validation_mae_comparison()
        self.experiment_visualizer.save_validation_rmse_comparison()
        self.experiment_visualizer.save_validation_r2_comparison()
        return result

    def download_dataset(self) -> Path:
        dataset_path = self.settings.data_dir / self.settings.dataset_filename
        if self.settings.dataset_source == DatasetSource.DOWNLOAD:
            self.data_lake_repository.download_latest_csv(dataset_path)
        else:
            logger.info("Using local dataset: path=%s", dataset_path)
        return dataset_path

    def prepare_dataset(self, dataset_path: Path) -> PreparedTrainingData:
        if self.dataset.path != dataset_path:
            raise ValueError(f"Dataset path does not match configured path: {self.dataset.path}")
        dataframe = self.dataset.training_frame(self.settings.target_column)
        target = dataframe.pop(self.settings.target_column)
        features = self.feature_builder_factory(dataframe).build()
        logger.info(
            f"Prepared training data: rows={len(dataframe)} features={len(features.columns)} target={self.settings.target_column}"
        )
        return PreparedTrainingData(features, target)

    def train_baseline(self, partitions: DatasetPartitions) -> BaselineModel:
        return BaselineModel().fit(partitions.train.features, partitions.train.target)

    def train_model(self, partitions: DatasetPartitions) -> HousePriceModel:
        return HousePriceModel(self.pipeline_builder).fit(partitions.train.features, partitions.train.target)

    def evaluate_model(self, trained_model, dataset_partition: DatasetPartition) -> RegressionMetrics:
        return self.evaluator.evaluate(
            dataset_partition.target,
            trained_model.predict(dataset_partition.features),
        ).metrics

    def evaluate_model_with_predictions(
            self,
            trained_model,
            dataset_partition: DatasetPartition,
    ) -> Evaluation:
        y_true = dataset_partition.target
        y_pred = trained_model.predict(dataset_partition.features)
        return self.evaluator.evaluate(y_true, y_pred)

    @staticmethod
    def _fitted_model_parameters(trained_model, configured_parameters: dict[str, object]) -> dict[str, object]:
        pipeline = getattr(trained_model, "pipeline", None)
        if pipeline is None or not hasattr(pipeline, "named_steps"):
            return configured_parameters
        regressor = pipeline.named_steps.get("regressor")
        if regressor is None or not hasattr(regressor, "get_params"):
            return configured_parameters
        parameters = regressor.get_params(deep=False)
        return parameters if isinstance(parameters, dict) else configured_parameters

    def save_model(self, trained_model: HousePriceModel, metadata: ModelMetadata) -> Path:
        return self.model_repository.save(
            trained_model.pipeline,
            self.settings.model_dir / self.settings.model_filename,
            metadata,
        )
