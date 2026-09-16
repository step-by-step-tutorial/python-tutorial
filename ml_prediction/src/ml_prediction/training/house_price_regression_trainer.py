import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ml_prediction.audit.report_event_data import (
    DatasetDownloaded, DatasetPrepared, DatasetSplit as DatasetSplitEvent,
    FeaturesBuilt, ModelEvaluated, ModelSaved, ModelTrained, TargetExtracted,
)
from ml_prediction.audit.experiment import Experiment
from ml_prediction.audit.model_metadata import ModelMetadata
from ml_prediction.audit.models import CURRENT_MODEL_VERSION, CURRENT_SCHEMA_VERSION
from ml_prediction.config.settings import TaskType, get_settings
from ml_prediction.data_model.dataset_split import DatasetSplit
from ml_prediction.data_model.evaluation import RegressionEvaluation
from ml_prediction.data_model.features_and_target import FeaturesAndTarget
from ml_prediction.data_model.regression_metrics import RegressionMetrics
from ml_prediction.dataset.dataset import Dataset
from ml_prediction.evaluation.regression_evaluator import RegressionEvaluator
from ml_prediction.experiment.experiment_coordinator import ExperimentCoordinator
from ml_prediction.features.feature_builder import FeatureBuilder
from ml_prediction.features.house_feature_model import HouseFeatureModel
from ml_prediction.model.trained_model import TrainedModel
from ml_prediction.model_selection.regression_model_selector import RegressionModelSelector
from ml_prediction.pipeline.regressor_builder import RegressorBuilder
from ml_prediction.pipeline.regressor_pipeline_builder import RegressorPipelineBuilder
from ml_prediction.presentation.experiment_data import ExperimentData
from ml_prediction.repository.local_model_repository import LocalModelRepository
from ml_prediction.training.dataset_splitter import DatasetSplitter
from ml_prediction.training.trainer import Trainer
from ml_prediction.utils.data_validator_utils import should_be_same

logger = logging.getLogger(__name__)


class HousePriceRegressionTrainer(Trainer[Experiment]):
    def __init__(self, dataset: Dataset) -> None:
        self._settings = get_settings(dataset.dataset_name)
        self._dataset = dataset
        self._feature_model = HouseFeatureModel()
        self._experiment_coordinator = ExperimentCoordinator(dataset.dataset_name)
        self._model_repository = LocalModelRepository()
        self._pipeline_builder = RegressorPipelineBuilder(self._feature_model, RegressorBuilder(dataset.dataset_name))
        self._evaluator = RegressionEvaluator()
        self._dataset_splitter = DatasetSplitter(dataset.dataset_name)
        self._search_enabled = self._settings.search_enabled
        self._model_selector = RegressionModelSelector()
        self._selected_model_parameters: dict[str, object] | None = None
        self._selected_model_score: float | None = None

    def train(self) -> Experiment:
        with self._experiment_coordinator:
            return self._train()

    def _train(self) -> Experiment:
        should_be_same(
            first=self._settings.task_type,
            second=TaskType.REGRESSION,
            error_message=(
                f"HousePriceRegressionTrainer supports only regression tasks, "
                f"got '{self._settings.task_type}'"
            ),
        )

        # Dataset preparation
        dataframe, dataset_path = self.download_dataset()
        experiment_id = self._experiment_coordinator.start(self._settings.model_parameters.as_dict())
        self._experiment_coordinator.log_artifact(dataset_path, "dataset")
        self._experiment_coordinator.record(DatasetDownloaded(dataset_path))

        # Feature engineering
        features_and_target = self.build_features_and_target(dataframe)
        self._experiment_coordinator.record(
            DatasetPrepared(len(features_and_target.features), self._settings.target_column))
        self._experiment_coordinator.record(
            FeaturesBuilt(len(features_and_target.features), len(features_and_target.features.columns)))
        self._experiment_coordinator.record(TargetExtracted(len(features_and_target.target), self._settings.target_column))

        # Train/validation/test split
        partitions = self._dataset_splitter.split(features_and_target.features, features_and_target.target)
        self._experiment_coordinator.record(DatasetSplitEvent(
            len(features_and_target.features),
            len(partitions.train.features),
            len(partitions.validation.features),
            len(partitions.test.features),
        ))

        # Experiment setup and monitoring
        experiment_timestamp = datetime.now(timezone.utc)
        configured_parameters = self._settings.model_parameters.as_dict()
        logger.info(
            f"Starting training experiment: "
            f"experiment_id={experiment_id} "
            f"model_type={self._settings.model_type} "
            f"model_parameters={configured_parameters}",
        )

        # Model training
        logger.info(
            f"Training model: model={self._settings.model_type} "
            f"partition=train rows={len(partitions.train.features)}",
        )
        trained_model = self.train_model(partitions)
        self._experiment_coordinator.record(
            ModelTrained("train", len(partitions.train.features), self._settings.model_type))

        # Evaluation
        logger.info(
            f"Evaluating model: model={self._settings.model_type} "
            f"partition=validation rows={len(partitions.validation.features)}",
        )
        validation_metrics = self.evaluate_model(trained_model, partitions.validation)
        self._experiment_coordinator.log_metrics("validation", validation_metrics)
        self._experiment_coordinator.record(ModelEvaluated(
            "validation",
            len(partitions.validation.features),
            self._settings.model_type,
            validation_metrics,
        ))

        # Prediction on the test partition
        logger.info(
            f"Predicting and evaluating model: model={self._settings.model_type} "
            f"partition=test rows={len(partitions.test.features)}",
        )
        final_test_evaluation = self.evaluate_model_with_predictions(trained_model, partitions.test)
        self._experiment_coordinator.log_metrics("test", final_test_evaluation.metrics)
        self._experiment_coordinator.record(ModelEvaluated(
            "test",
            len(partitions.test.features),
            self._settings.model_type,
            final_test_evaluation.metrics,
        ))

        # Model persistence
        metadata = ModelMetadata(
            model_type=self._settings.model_type,
            model_parameters=self._selected_model_parameters or configured_parameters,
            target_column=self._settings.target_column,
            numeric_features=self._feature_model.get_numeric_features(),
            boolean_features=self._feature_model.get_boolean_features(),
            categorical_features=self._feature_model.get_categorical_features(),
            training_timestamp=experiment_timestamp,
            validation_metrics=validation_metrics,
            final_test_metrics=final_test_evaluation.metrics,
            schema_version=CURRENT_SCHEMA_VERSION,
            model_version=CURRENT_MODEL_VERSION,
            dataset_name=self._settings.dataset_name,
            task_type=self._settings.task_type.value,
            prediction_column=self._settings.prediction_column,
        )
        model_path = self.save_model(trained_model, metadata)
        self._experiment_coordinator.log_model(trained_model.pipeline)
        self._experiment_coordinator.log_artifact(model_path.with_suffix(".metadata.json"), "model")
        self._experiment_coordinator.record(ModelSaved(model_path))

        # Experiments, visualizations, and monitoring
        result = Experiment(
            experiment_id=experiment_id,
            timestamp=experiment_timestamp,
            dataset_name=self._settings.dataset_name,
            model_type=self._settings.model_type,
            model_parameters=metadata.model_parameters,
            validation_metrics=validation_metrics,
            test_metrics=final_test_evaluation.metrics,
            model_path=model_path,
            report_path=self._experiment_coordinator.report_path,
            model_selection_metric="mean_absolute_error" if self._search_enabled else None,
            model_selection_score=self._selected_model_score,
        )
        self._experiment_coordinator.publish(ExperimentData(
            model=trained_model,
            evaluation=final_test_evaluation,
            report_dir=self._settings.report_dir,
        ))
        self._experiment_coordinator.complete(result)
        return result

    def download_dataset(self) -> tuple[pd.DataFrame, Path]:
        return self._dataset.download()

    def build_features_and_target(self, dataframe: pd.DataFrame) -> FeaturesAndTarget:
        dataframe = dataframe.dropna(subset=[self._settings.target_column]).copy()

        target = dataframe.pop(self._settings.target_column)
        features = FeatureBuilder(dataframe, self._feature_model).build()
        logger.info(
            f"Prepared training data: "
            f"rows={len(dataframe)} "
            f"features={len(features.columns)} "
            f"target={self._settings.target_column}"
        )
        return FeaturesAndTarget(features, target)

    def train_model(self, partitions: DatasetSplit) -> TrainedModel:
        if not self._search_enabled:
            return TrainedModel(self._pipeline_builder).fit(partitions.train.features, partitions.train.target)

        pipeline = TrainedModel(self._pipeline_builder).pipeline
        selection = self._model_selector.select(
            pipeline,
            partitions.train.features,
            partitions.train.target,
        )
        self._selected_model_parameters = {
            key.removeprefix("regressor__"): value for key, value in selection.parameters.items()
        }
        self._selected_model_score = selection.mean_absolute_error
        return TrainedModel.from_pipeline(selection.pipeline)

    def evaluate_model(self, model, data: FeaturesAndTarget) -> RegressionMetrics:
        return self._evaluator.evaluate(data.target, model.predict(data.features)).metrics

    def evaluate_model_with_predictions(self, model, data: FeaturesAndTarget) -> RegressionEvaluation:
        y_true = data.target
        y_pred = model.predict(data.features)
        return self._evaluator.evaluate(y_true, y_pred)

    def save_model(self, model: TrainedModel, metadata: ModelMetadata) -> Path:
        return self._model_repository.save(
            model.pipeline,
            self._settings.model_dir / self._settings.model_filename,
            metadata,
        )
