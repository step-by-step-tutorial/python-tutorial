import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd

from ml_prediction.config.settings import get_settings
from ml_prediction.config.settings_types import TaskType
from ml_prediction.data_model.classification_evaluation import ClassificationEvaluation
from ml_prediction.data_model.classification_metrics import ClassificationMetrics
from ml_prediction.data_model.dataset_split import DatasetSplit
from ml_prediction.data_model.dataset_subset import DatasetSubset
from ml_prediction.data_model.experiment import Experiment
from ml_prediction.data_model.features_and_target import FeaturesAndTarget
from ml_prediction.data_model.model_metadata import CURRENT_MODEL_VERSION, CURRENT_SCHEMA_VERSION, ModelMetadata
from ml_prediction.dataset.dataset import Dataset
from ml_prediction.evaluation.classification_evaluator import ClassificationEvaluator
from ml_prediction.features.feature_builder import FeatureBuilder
from ml_prediction.features.online_shopping_feature_model import OnlineShoppingFeatureModel
from ml_prediction.model.classification_model import ClassificationModel
from ml_prediction.model_selection.classification_model_selector import ClassificationModelSelector
from ml_prediction.pipeline.classification_pipeline_builder import ClassificationPipelineBuilder
from ml_prediction.pipeline.classifier_builder import ClassifierBuilder
from ml_prediction.reporting.experiment_service import ExperimentService
from ml_prediction.reporting.mlflow_tracker import MlflowTracker
from ml_prediction.reporting.report_service import ReportService
from ml_prediction.repository.local_model_repository import LocalModelRepository
from ml_prediction.training.dataset_splitter import DatasetSplitter
from ml_prediction.training.trainer import Trainer

logger = logging.getLogger(__name__)


class OnlineShoppingClassificationTrainer(Trainer[Experiment]):
    def __init__(self, dataset: Dataset, search_enabled: bool = False) -> None:
        self._settings = get_settings(dataset.dataset_name)
        self._dataset = dataset
        self._feature_model = OnlineShoppingFeatureModel()
        self._pipeline_builder = ClassificationPipelineBuilder(
            self._feature_model,
            ClassifierBuilder(dataset.dataset_name),
        )
        self._evaluator = ClassificationEvaluator()
        self._dataset_splitter = DatasetSplitter(dataset.dataset_name)
        self._model_repository = LocalModelRepository()
        self._experiment_service = ExperimentService(dataset.dataset_name)
        self._mlflow_tracker = MlflowTracker(self._settings)
        self._report_service = ReportService(self._settings.report_dir)
        self._search_enabled = search_enabled
        self._model_selector = ClassificationModelSelector()
        self._selected_model_parameters: dict[str, object] | None = None
        self._selected_model_score: float | None = None

    def train(self) -> Experiment:
        if self._settings.task_type != TaskType.CLASSIFICATION:
            raise ValueError("OnlineShoppingClassificationTrainer requires a classification dataset")
        dataframe, dataset_path = self.download_dataset()
        prepared = self.build_features_and_target(dataframe)
        partitions = self._dataset_splitter.split(prepared.features, prepared.target)
        experiment_id = str(uuid4())
        self._mlflow_tracker.start(experiment_id, {
            "n_estimators": self._settings.n_estimators,
            "n_jobs": self._settings.n_jobs,
            "max_depth": self._settings.max_depth,
            "min_samples_split": self._settings.min_samples_split,
            "min_samples_leaf": self._settings.min_samples_leaf,
            "max_features": self._settings.max_features,
            "bootstrap": self._settings.bootstrap,
            "random_state": self._settings.random_state,
        })
        self._mlflow_tracker.log_artifact(dataset_path, "dataset")
        model = self.train_model(partitions)
        validation = self.evaluate_model(model, partitions.validation)
        self._mlflow_tracker.log_metrics("validation", validation)
        final = self.evaluate_model_with_predictions(model, partitions.test)
        self._mlflow_tracker.log_metrics("test", final.metrics)
        timestamp = datetime.now(timezone.utc)
        model_parameters = {
            "n_estimators": self._settings.n_estimators,
            "n_jobs": self._settings.n_jobs,
            "max_depth": self._settings.max_depth,
            "min_samples_split": self._settings.min_samples_split,
            "min_samples_leaf": self._settings.min_samples_leaf,
            "max_features": self._settings.max_features,
            "bootstrap": self._settings.bootstrap,
            "random_state": self._settings.random_state,
        }
        metadata = ModelMetadata(
            model_type=self._settings.model_type,
            model_parameters=self._selected_model_parameters or model_parameters,
            target_column=self._settings.target_column,
            numeric_features=self._feature_model.get_numeric_features(),
            boolean_features=self._feature_model.get_boolean_features(),
            categorical_features=self._feature_model.get_categorical_features(),
            training_timestamp=timestamp,
            validation_metrics=validation,
            final_test_metrics=final.metrics,
            schema_version=CURRENT_SCHEMA_VERSION,
            model_version=CURRENT_MODEL_VERSION,
            dataset_name=self._settings.dataset_name,
            task_type=self._settings.task_type.value,
            prediction_column=self._settings.prediction_column,
        )
        model_path = self.save_model(model, metadata)
        self._mlflow_tracker.log_model(model.pipeline)
        self._mlflow_tracker.log_artifact(model_path.with_suffix(".metadata.json"), "model")
        report = self._report_service.start(self._settings.dataset_name, "training", model_path)
        report.record("training_completed", rows=len(dataframe), details=str(dataset_path))
        result = Experiment(
            experiment_id=experiment_id, timestamp=timestamp, dataset_name=self._settings.dataset_name,
            model_type=self._settings.model_type, model_parameters=metadata.model_parameters,
            validation_metrics=validation, test_metrics=final.metrics,
            model_path=model_path, report_path=report.path,
            model_selection_metric="f1_weighted" if self._search_enabled else None,
            model_selection_score=self._selected_model_score,
        )
        self._experiment_service.save(result)
        self._mlflow_tracker.log_artifact(report.path, "reports")
        self._mlflow_tracker.end()
        return result

    def download_dataset(self) -> tuple[pd.DataFrame, Path]:
        return self._dataset.download()

    def build_features_and_target(self, dataframe: pd.DataFrame) -> FeaturesAndTarget:
        dataframe = dataframe.dropna(subset=[self._settings.target_column]).copy()
        target = dataframe.pop(self._settings.target_column)
        return FeaturesAndTarget(FeatureBuilder(dataframe, self._feature_model).build(), target)

    def train_model(self, partitions: DatasetSplit) -> ClassificationModel:
        if not self._search_enabled:
            return ClassificationModel(self._pipeline_builder).fit(
                partitions.train.features,
                partitions.train.target,
            )

        pipeline = ClassificationModel(self._pipeline_builder).pipeline
        selection = self._model_selector.select(
            pipeline,
            partitions.train.features,
            partitions.train.target,
        )
        self._selected_model_parameters = {
            key.removeprefix("classifier__"): value
            for key, value in selection.parameters.items()
        }
        self._selected_model_score = selection.f1_score
        return ClassificationModel.from_pipeline(selection.pipeline)

    def evaluate_model(self, trained_model, dataset_partition: DatasetSubset) -> ClassificationMetrics:
        return self._evaluator.evaluate(
            dataset_partition.target, trained_model.predict(dataset_partition.features)
        ).metrics

    def evaluate_model_with_predictions(
            self, trained_model, dataset_partition: DatasetSubset
    ) -> ClassificationEvaluation:
        y_true = dataset_partition.target
        y_pred = trained_model.predict(dataset_partition.features)
        return self._evaluator.evaluate(y_true, y_pred)

    def save_model(self, trained_model: ClassificationModel, metadata: ModelMetadata) -> Path:
        return self._model_repository.save(
            trained_model.pipeline,
            self._settings.model_dir / self._settings.model_filename,
            metadata,
        )
