import logging
from dataclasses import asdict
from ml_prediction.audit.data.experiment_audit_data import ExperimentAuditData
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ml_prediction.audit.pipeline_step.dataset_downloaded_data import DatasetDownloadedData
from ml_prediction.audit.pipeline_step.dataset_prepared_data import DatasetPreparedData
from ml_prediction.audit.pipeline_step.dataset_split_data import DatasetSplitData as AuditDatasetSplitData
from ml_prediction.audit.pipeline_step.features_built_data import FeaturesBuiltData
from ml_prediction.audit.pipeline_step.model_evaluated_data import ModelEvaluatedData
from ml_prediction.audit.pipeline_step.model_saved_data import ModelSavedData
from ml_prediction.audit.pipeline_step.model_training_data import ModelTrainingData
from ml_prediction.audit.pipeline_step.target_extracted_data import TargetExtractedData
from ml_prediction.audit.data.artifact_data import ArtifactData
from ml_prediction.audit.data.metrics_data import MetricsData
from ml_prediction.audit.data.trained_model_data import TrainedModelData
from ml_prediction.audit.data.experiment_data import ExperimentData
from ml_prediction.audit.data.experiment_task_type import ExperimentTaskType
from ml_prediction.audit.data.metadata import Metadata
from ml_prediction.audit.data.metadata import CURRENT_MODEL_VERSION, CURRENT_SCHEMA_VERSION
from ml_prediction.config.settings import get_settings
from ml_prediction.data_model.classification_evaluation_data import ClassificationEvaluationData
from ml_prediction.data_model.classification_metrics import ClassificationMetrics
from ml_prediction.data_model.dataset_split import DatasetSplitData
from ml_prediction.data_model.features_and_target import FeaturesAndTarget
from ml_prediction.dataset.dataset import Dataset
from ml_prediction.evaluation.classification_evaluator import ClassificationEvaluator
from ml_prediction.audit.audit_service import AuditService
from ml_prediction.presentation.visualizer import VisualizationFacade
from ml_prediction.features.feature_builder import FeatureBuilder
from ml_prediction.features.online_shopping_feature_model import OnlineShoppingFeatureModel
from ml_prediction.model.trained_model import TrainedModel
from ml_prediction.model_selection.classification_model_selector import ClassificationModelSelector
from ml_prediction.pipeline.classification_pipeline_builder import ClassificationPipelineBuilder
from ml_prediction.pipeline.classifier_builder import ClassifierBuilder
from ml_prediction.repository.local_model_repository import LocalModelRepository
from ml_prediction.training.dataset_splitter import DatasetSplitter
from ml_prediction.training.trainer import Trainer

logger = logging.getLogger(__name__)


class OnlineShoppingClassificationTrainer(Trainer[ExperimentData]):
    def __init__(self, dataset: Dataset) -> None:
        self._settings = get_settings(dataset.dataset_name)
        self._dataset = dataset
        self._feature_model = OnlineShoppingFeatureModel()
        self._pipeline_builder = ClassificationPipelineBuilder(self._feature_model,
                                                               ClassifierBuilder(dataset.dataset_name))
        self._evaluator = ClassificationEvaluator()
        self._dataset_splitter = DatasetSplitter(dataset.dataset_name)
        self._model_repository = LocalModelRepository()
        self._audit_service = AuditService(dataset.dataset_name)
        self._visualization_facade = VisualizationFacade(dataset.dataset_name)
        self._search_enabled = self._settings.search_enabled
        self._model_selector = ClassificationModelSelector()
        self._selected_model_parameters: dict[str, object] | None = None
        self._selected_model_score: float | None = None

    def train(self) -> ExperimentData:
        return self._train()

    def _train(self) -> ExperimentData:
        if self._settings.task_type != ExperimentTaskType.CLASSIFICATION:
            raise ValueError("OnlineShoppingClassificationTrainer requires a classification dataset")
        dataframe, dataset_path = self.download_dataset()
        configured_parameters = self._settings.model_parameters.as_dict()
        run_id = self._audit_service.run_id
        self._audit_service.write(ArtifactData(dataset_path, "dataset"))
        self._audit_service.write(DatasetDownloadedData(dataset_path))
        prepared = self.build_features_and_target(dataframe)
        self._audit_service.write(DatasetPreparedData(len(prepared.features), self._settings.target_column))
        self._audit_service.write(FeaturesBuiltData(len(prepared.features), len(prepared.features.columns)))
        self._audit_service.write(TargetExtractedData(len(prepared.target), self._settings.target_column))
        partitions = self._dataset_splitter.split(prepared.features, prepared.target)
        self._audit_service.write(AuditDatasetSplitData(
            len(prepared.features),
            len(partitions.train.features),
            len(partitions.validation.features),
            len(partitions.test.features),
        ))
        model = self.train_model(partitions)
        self._audit_service.write(
            ModelTrainingData("train", len(partitions.train.features), self._settings.model_type))
        validation = self.evaluate_model(model, partitions.validation)
        self._audit_service.write(MetricsData("validation", validation))
        self._audit_service.write(ModelEvaluatedData(
            "validation",
            len(partitions.validation.features),
            self._settings.model_type,
            validation,
        ))
        final = self.evaluate_model_with_predictions(model, partitions.test)
        self._audit_service.write(MetricsData("test", final.metrics))
        self._audit_service.write(ModelEvaluatedData(
            "test",
            len(partitions.test.features),
            self._settings.model_type,
            final.metrics,
        ))
        timestamp = datetime.now(timezone.utc)
        metadata = Metadata(
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
        self._audit_service.write(TrainedModelData(model.pipeline))
        self._audit_service.write(ArtifactData(model_path.with_suffix(".metadata.json"), "model"))
        self._audit_service.write(ModelSavedData(model_path))
        result = ExperimentData(
            run_id=run_id, timestamp=timestamp, dataset_name=self._settings.dataset_name,
            model_type=self._settings.model_type, model_parameters=metadata.model_parameters,
            validation_metrics=validation, test_metrics=final.metrics,
            model_path=model_path, audit_path=None,
            task_type=ExperimentTaskType.value_of(self._settings.task_type.value),
            model_selection_metric="f1_weighted" if self._search_enabled else None,
            model_selection_score=self._selected_model_score,
        )
        audit_data = ExperimentAuditData(
            experiment=result,
            model=model,
            evaluation=final,
            audit_dir=self._settings.audit_dir,
            metrics={
                **{f"validation_{key}": float(value) for key, value in asdict(validation).items()},
                **{f"test_{key}": float(value) for key, value in asdict(final.metrics).items()},
            },
        )
        self._audit_service.write(self._visualization_facade.visualize(audit_data))
        return result

    def download_dataset(self) -> tuple[pd.DataFrame, Path]:
        return self._dataset.download()

    def build_features_and_target(self, dataframe: pd.DataFrame) -> FeaturesAndTarget:
        dataframe = dataframe.dropna(subset=[self._settings.target_column]).copy()
        target = dataframe.pop(self._settings.target_column)
        return FeaturesAndTarget(FeatureBuilder(dataframe, self._feature_model).build(), target)

    def train_model(self, partitions: DatasetSplitData) -> TrainedModel:
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

    def evaluate_model_with_predictions(self, model, data: FeaturesAndTarget) -> ClassificationEvaluationData:
        y_true = data.target
        y_pred = model.predict(data.features)
        return self._evaluator.evaluate(y_true, y_pred)

    def save_model(self, model: TrainedModel, metadata: Metadata) -> Path:
        return self._model_repository.save(
            model.pipeline,
            self._settings.model_dir / self._settings.model_filename,
            metadata,
        )
