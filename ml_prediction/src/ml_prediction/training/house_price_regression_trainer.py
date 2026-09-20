import logging
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ml_prediction.audit.audit_service import AuditService
from ml_prediction.audit.data.artifact_category import ArtifactCategory
from ml_prediction.audit.data.artifact_data import ArtifactData
from ml_prediction.audit.data.experiment_data import ExperimentData
from ml_prediction.audit.data.experiment_task_type import ExperimentTaskType
from ml_prediction.audit.data.metadata import CURRENT_MODEL_VERSION, CURRENT_SCHEMA_VERSION
from ml_prediction.audit.data.metadata import Metadata
from ml_prediction.audit.data.metrics_data import MetricsData
from ml_prediction.audit.data.trained_model_data import TrainedModelData
from ml_prediction.audit.data.training_audit_data import TrainingAuditData
from ml_prediction.audit.pipeline_step.dataset_downloaded_data import DatasetDownloadedData
from ml_prediction.audit.pipeline_step.dataset_prepared_data import DatasetPreparedData
from ml_prediction.audit.pipeline_step.dataset_split_data import DatasetSplitData as AuditDatasetSplitData
from ml_prediction.audit.pipeline_step.features_built_data import FeaturesBuiltData
from ml_prediction.audit.pipeline_step.model_evaluated_data import ModelEvaluatedData
from ml_prediction.audit.pipeline_step.model_saved_data import ModelSavedData
from ml_prediction.audit.pipeline_step.model_training_data import ModelTrainingData
from ml_prediction.audit.pipeline_step.target_extracted_data import TargetExtractedData
from ml_prediction.config.settings import get_settings
from ml_prediction.data_model.dataset_split import DatasetSplitData
from ml_prediction.data_model.evaluation_data import RegressionEvaluationData
from ml_prediction.data_model.features_and_target import FeaturesAndTarget
from ml_prediction.data_model.regression_metrics import RegressionMetrics
from ml_prediction.dataset.dataset import Dataset
from ml_prediction.evaluation.regression_evaluator import RegressionEvaluator
from ml_prediction.features.feature_builder import FeatureBuilder
from ml_prediction.features.house_feature_model import HouseFeatureModel
from ml_prediction.model.trained_model import TrainedModel
from ml_prediction.model_selection.regression_model_selector import RegressionModelSelector
from ml_prediction.pipeline.regressor_builder import RegressorBuilder
from ml_prediction.pipeline.regressor_pipeline_builder import RegressorPipelineBuilder
from ml_prediction.presentation.visualizer import VisualizationFacade
from ml_prediction.repository.local_model_repository import LocalModelRepository
from ml_prediction.training.dataset_splitter import DatasetSplitter
from ml_prediction.training.trainer import Trainer
from ml_prediction.utils.data_validator_utils import should_be_same

logger = logging.getLogger(__name__)


class HousePriceRegressionTrainer(Trainer[ExperimentData]):
    def __init__(self, dataset: Dataset) -> None:
        self._settings = get_settings(dataset.dataset_name)
        self._dataset = dataset
        self._feature_model = HouseFeatureModel()
        self._audit_service = AuditService(dataset.dataset_name)
        self._visualization_facade = VisualizationFacade(dataset.dataset_name)
        self._model_repository = LocalModelRepository()
        self._pipeline_builder = RegressorPipelineBuilder(self._feature_model, RegressorBuilder(dataset.dataset_name))
        self._evaluator = RegressionEvaluator()
        self._dataset_splitter = DatasetSplitter(dataset.dataset_name)
        self._search_enabled = self._settings.search_enabled
        self._model_selector = RegressionModelSelector()
        self._selected_model_parameters: dict[str, object] | None = None
        self._selected_model_score: float | None = None

    def train(self) -> ExperimentData:
        return self._train()

    def _train(self) -> ExperimentData:
        should_be_same(
            first=self._settings.task_type,
            second=ExperimentTaskType.REGRESSION,
            error_message=(
                f"HousePriceRegressionTrainer supports only regression tasks, "
                f"got '{self._settings.task_type}'"
            ),
        )

        # Dataset preparation
        dataframe, dataset_path = self.download_dataset()
        run_id = self._audit_service.run_id
        self._audit_service.write(ArtifactData(dataset_path, ArtifactCategory.DATASET))
        self._audit_service.write(DatasetDownloadedData(dataset_path))

        # Feature engineering
        features_and_target = self.build_features_and_target(dataframe)
        self._audit_service.write(
            DatasetPreparedData(len(features_and_target.features), self._settings.target_column))
        self._audit_service.write(
            FeaturesBuiltData(len(features_and_target.features), len(features_and_target.features.columns)))
        self._audit_service.write(TargetExtractedData(len(features_and_target.target), self._settings.target_column))

        # Train/validation/test split
        partitions = self._dataset_splitter.split(features_and_target.features, features_and_target.target)
        self._audit_service.write(AuditDatasetSplitData(
            len(features_and_target.features),
            len(partitions.train.features),
            len(partitions.validation.features),
            len(partitions.test.features),
        ))

        # ExperimentData setup and monitoring
        experiment_timestamp = datetime.now(timezone.utc)
        configured_parameters = self._settings.model_parameters.as_dict()
        logger.info(
            f"Starting training experiment: "
            f"run_id={run_id} "
            f"model_type={self._settings.model_type} "
            f"model_parameters={configured_parameters}",
        )

        # Model training
        logger.info(
            f"Training model: model={self._settings.model_type} "
            f"partition=train rows={len(partitions.train.features)}",
        )
        trained_model = self.train_model(partitions)
        self._audit_service.write(
            ModelTrainingData("train", len(partitions.train.features), self._settings.model_type))

        # Evaluation
        logger.info(
            f"Evaluating model: model={self._settings.model_type} "
            f"partition=validation rows={len(partitions.validation.features)}",
        )
        validation_metrics = self.evaluate_model(trained_model, partitions.validation)
        self._audit_service.write(MetricsData("validation", validation_metrics))
        self._audit_service.write(ModelEvaluatedData(
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
        self._audit_service.write(MetricsData("test", final_test_evaluation.metrics))
        self._audit_service.write(ModelEvaluatedData(
            "test",
            len(partitions.test.features),
            self._settings.model_type,
            final_test_evaluation.metrics,
        ))

        # Model persistence
        metadata = Metadata(
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
        self._audit_service.write(TrainedModelData(trained_model.pipeline))
        self._audit_service.write(ArtifactData(model_path.with_suffix(".metadata.json"), ArtifactCategory.MODEL))
        self._audit_service.write(ModelSavedData(model_path))

        # Experiments, visualizations, and monitoring
        result = ExperimentData(
            run_id=run_id,
            timestamp=experiment_timestamp,
            dataset_name=self._settings.dataset_name,
            model_type=self._settings.model_type,
            model_parameters=metadata.model_parameters,
            validation_metrics=validation_metrics,
            test_metrics=final_test_evaluation.metrics,
            model_path=model_path,
            audit_path=None,
            task_type=ExperimentTaskType.value_of(self._settings.task_type.value),
            model_selection_metric="mean_absolute_error" if self._search_enabled else None,
            model_selection_score=self._selected_model_score,
        )
        audit_data = TrainingAuditData(
            experiment=result,
            model=trained_model,
            evaluation=final_test_evaluation,
            path=self._settings.audit_dir,
            metrics={
                **{f"validation_{key}": float(value) for key, value in asdict(validation_metrics).items()},
                **{f"test_{key}": float(value) for key, value in asdict(final_test_evaluation.metrics).items()},
            },
        )
        self._audit_service.write(self._visualization_facade.visualize(audit_data))
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

    def train_model(self, partitions: DatasetSplitData) -> TrainedModel:
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

    def evaluate_model_with_predictions(self, model, data: FeaturesAndTarget) -> RegressionEvaluationData:
        y_true = data.target
        y_pred = model.predict(data.features)
        return self._evaluator.evaluate(y_true, y_pred)

    def save_model(self, model: TrainedModel, metadata: Metadata) -> Path:
        model_path = self._settings.model_dir / self._settings.model_filename
        self._model_repository.save_model(model_path, model.pipeline, metadata)
        return model_path
