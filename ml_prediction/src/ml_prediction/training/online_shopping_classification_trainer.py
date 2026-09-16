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
from ml_prediction.config.settings import get_settings
from ml_prediction.config.settings_types import TaskType
from ml_prediction.data_model.classification_evaluation import ClassificationEvaluation
from ml_prediction.data_model.classification_metrics import ClassificationMetrics
from ml_prediction.data_model.dataset_split import DatasetSplit
from ml_prediction.data_model.features_and_target import FeaturesAndTarget
from ml_prediction.dataset.dataset import Dataset
from ml_prediction.evaluation.classification_evaluator import ClassificationEvaluator
from ml_prediction.experiment.experiment_coordinator import ExperimentCoordinator
from ml_prediction.features.feature_builder import FeatureBuilder
from ml_prediction.features.online_shopping_feature_model import OnlineShoppingFeatureModel
from ml_prediction.model.trained_model import TrainedModel
from ml_prediction.model_selection.classification_model_selector import ClassificationModelSelector
from ml_prediction.pipeline.classification_pipeline_builder import ClassificationPipelineBuilder
from ml_prediction.pipeline.classifier_builder import ClassifierBuilder
from ml_prediction.presentation.experiment_data import ExperimentData
from ml_prediction.repository.local_model_repository import LocalModelRepository
from ml_prediction.training.dataset_splitter import DatasetSplitter
from ml_prediction.training.trainer import Trainer

logger = logging.getLogger(__name__)


class OnlineShoppingClassificationTrainer(Trainer[Experiment]):
    def __init__(self, dataset: Dataset) -> None:
        self._settings = get_settings(dataset.dataset_name)
        self._dataset = dataset
        self._feature_model = OnlineShoppingFeatureModel()
        self._pipeline_builder = ClassificationPipelineBuilder(self._feature_model,
                                                               ClassifierBuilder(dataset.dataset_name))
        self._evaluator = ClassificationEvaluator()
        self._dataset_splitter = DatasetSplitter(dataset.dataset_name)
        self._model_repository = LocalModelRepository()
        self._experiment_coordinator = ExperimentCoordinator(dataset.dataset_name)
        self._search_enabled = self._settings.search_enabled
        self._model_selector = ClassificationModelSelector()
        self._selected_model_parameters: dict[str, object] | None = None
        self._selected_model_score: float | None = None

    def train(self) -> Experiment:
        return self._experiment_coordinator.execute(
            self._train,
            self._settings.model_parameters.as_dict(),
        )

    def _train(self) -> Experiment:
        if self._settings.task_type != TaskType.CLASSIFICATION:
            raise ValueError("OnlineShoppingClassificationTrainer requires a classification dataset")
        dataframe, dataset_path = self.download_dataset()
        configured_parameters = self._settings.model_parameters.as_dict()
        experiment_id = self._experiment_coordinator.experiment_id
        self._experiment_coordinator.log_artifact(dataset_path, "dataset")
        self._experiment_coordinator.record(DatasetDownloaded(dataset_path))
        prepared = self.build_features_and_target(dataframe)
        self._experiment_coordinator.record(DatasetPrepared(len(prepared.features), self._settings.target_column))
        self._experiment_coordinator.record(FeaturesBuilt(len(prepared.features), len(prepared.features.columns)))
        self._experiment_coordinator.record(TargetExtracted(len(prepared.target), self._settings.target_column))
        partitions = self._dataset_splitter.split(prepared.features, prepared.target)
        self._experiment_coordinator.record(DatasetSplitEvent(
            len(prepared.features),
            len(partitions.train.features),
            len(partitions.validation.features),
            len(partitions.test.features),
        ))
        model = self.train_model(partitions)
        self._experiment_coordinator.record(
            ModelTrained("train", len(partitions.train.features), self._settings.model_type))
        validation = self.evaluate_model(model, partitions.validation)
        self._experiment_coordinator.log_metrics("validation", validation)
        self._experiment_coordinator.record(ModelEvaluated(
            "validation",
            len(partitions.validation.features),
            self._settings.model_type,
            validation,
        ))
        final = self.evaluate_model_with_predictions(model, partitions.test)
        self._experiment_coordinator.log_metrics("test", final.metrics)
        self._experiment_coordinator.record(ModelEvaluated(
            "test",
            len(partitions.test.features),
            self._settings.model_type,
            final.metrics,
        ))
        timestamp = datetime.now(timezone.utc)
        metadata = ModelMetadata(
            model_type=self._settings.model_type,
            model_parameters=self._selected_model_parameters or configured_parameters,
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
        self._experiment_coordinator.log_model(model.pipeline)
        self._experiment_coordinator.log_artifact(model_path.with_suffix(".metadata.json"), "model")
        self._experiment_coordinator.record(ModelSaved(model_path))
        result = Experiment(
            experiment_id=experiment_id, timestamp=timestamp, dataset_name=self._settings.dataset_name,
            model_type=self._settings.model_type, model_parameters=metadata.model_parameters,
            validation_metrics=validation, test_metrics=final.metrics,
            model_path=model_path, report_path=self._experiment_coordinator.report_path,
            model_selection_metric="f1_weighted" if self._search_enabled else None,
            model_selection_score=self._selected_model_score,
        )
        self._experiment_coordinator.publish(ExperimentData(
            model=model,
            evaluation=final,
            report_dir=self._settings.report_dir,
        ))
        return result

    def download_dataset(self) -> tuple[pd.DataFrame, Path]:
        return self._dataset.download()

    def build_features_and_target(self, dataframe: pd.DataFrame) -> FeaturesAndTarget:
        dataframe = dataframe.dropna(subset=[self._settings.target_column]).copy()
        target = dataframe.pop(self._settings.target_column)
        return FeaturesAndTarget(FeatureBuilder(dataframe, self._feature_model).build(), target)

    def train_model(self, partitions: DatasetSplit) -> TrainedModel:
        if not self._search_enabled:
            return TrainedModel(self._pipeline_builder).fit(
                partitions.train.features,
                partitions.train.target,
            )

        pipeline = TrainedModel(self._pipeline_builder).pipeline
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
        return TrainedModel.from_pipeline(selection.pipeline)

    def evaluate_model(self, model, data: FeaturesAndTarget) -> ClassificationMetrics:
        return self._evaluator.evaluate(
            data.target, model.predict(data.features)
        ).metrics

    def evaluate_model_with_predictions(self, model, data: FeaturesAndTarget) -> ClassificationEvaluation:
        y_true = data.target
        y_pred = model.predict(data.features)
        return self._evaluator.evaluate(y_true, y_pred)

    def save_model(self, model: TrainedModel, metadata: ModelMetadata) -> Path:
        return self._model_repository.save(
            model.pipeline,
            self._settings.model_dir / self._settings.model_filename,
            metadata,
        )
