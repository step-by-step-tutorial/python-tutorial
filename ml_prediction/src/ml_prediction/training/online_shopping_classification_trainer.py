import logging
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from ml_prediction.audit.audit_service import AuditService
from ml_prediction.audit.data.artifact_category import ArtifactCategory
from ml_prediction.audit.data.artifact_dto import ArtifactDto
from ml_prediction.audit.data.experiment_dto import ExperimentDto
from ml_prediction.audit.data.experiment_task_type import ExperimentTaskType
from ml_prediction.audit.data.metadata_dto import CURRENT_MODEL_VERSION, CURRENT_SCHEMA_VERSION
from ml_prediction.audit.data.metadata_dto import MetadataDto
from ml_prediction.audit.data.metrics_dto import MetricsDto
from ml_prediction.audit.data.trained_model_dto import TrainedModelDto
from ml_prediction.audit.data.training_audit_dto import TrainingAuditDto
from ml_prediction.audit.pipeline_step.dataset_downloaded_dto import DatasetDownloadedDto
from ml_prediction.audit.pipeline_step.dataset_prepared_dto import DatasetPreparedDto
from ml_prediction.audit.pipeline_step.dataset_split_dto import DatasetSplitDto as AuditDatasetSplitDto
from ml_prediction.audit.pipeline_step.features_built_dto import FeaturesBuiltDto
from ml_prediction.audit.pipeline_step.model_evaluated_dto import ModelEvaluatedDto
from ml_prediction.audit.pipeline_step.model_saved_dto import ModelSavedDto
from ml_prediction.audit.pipeline_step.model_training_dto import ModelTrainingDto
from ml_prediction.audit.pipeline_step.target_extracted_dto import TargetExtractedDto
from ml_prediction.config.settings import get_settings
from ml_prediction.data_model.classification_metrics import ClassificationMetrics
from ml_prediction.data_model.dataset_split_dto import DatasetSplitDto
from ml_prediction.data_model.evaluation_dto import EvaluationDto
from ml_prediction.data_model.features_and_target import FeaturesAndTarget
from ml_prediction.dataset.dataset import Dataset
from ml_prediction.evaluation.classification_evaluator import ClassificationEvaluator
from ml_prediction.features.feature_builder import FeatureBuilder
from ml_prediction.features.online_shopping_feature_model import OnlineShoppingFeatureModel
from ml_prediction.model.trained_model import TrainedModel
from ml_prediction.model_selection.classification_model_selector import ClassificationModelSelector
from ml_prediction.pipeline.classification_pipeline_builder import ClassificationPipelineBuilder
from ml_prediction.pipeline.classifier_builder import ClassifierBuilder
from ml_prediction.pipeline.pipeline_step import PipelineStep
from ml_prediction.visualize.visualizer_facade import VisualizationFacade
from ml_prediction.repository.local_model_repository import LocalModelRepository
from ml_prediction.training.dataset_splitter import DatasetSplitter
from ml_prediction.training.trainer import Trainer

logger = logging.getLogger(__name__)


class OnlineShoppingClassificationTrainer(Trainer[ExperimentDto]):
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

    def train(self) -> ExperimentDto:
        return self._train()

    def _train(self) -> ExperimentDto:
        if self._settings.task_type != ExperimentTaskType.CLASSIFICATION:
            raise ValueError("OnlineShoppingClassificationTrainer requires a classification dataset")
        dataframe, dataset_path = self.download_dataset()
        configured_parameters = self._settings.model_parameters.to_dict()
        run_id = self._audit_service.run_id
        self._audit_service.write(ArtifactDto(dataset_path, ArtifactCategory.DATASET))
        self._audit_service.write(DatasetDownloadedDto(dataset_path))
        prepared = self.build_features_and_target(dataframe)
        self._audit_service.write(DatasetPreparedDto(len(prepared.features), self._settings.target_column))
        self._audit_service.write(FeaturesBuiltDto(len(prepared.features), len(prepared.features.columns)))
        self._audit_service.write(TargetExtractedDto(len(prepared.target), self._settings.target_column))
        partitions = self._dataset_splitter.split(prepared.features, prepared.target)
        self._audit_service.write(AuditDatasetSplitDto(
            len(prepared.features),
            len(partitions.train.features),
            len(partitions.validation.features),
            len(partitions.test.features),
        ))
        model = self.train_model(partitions)
        self._audit_service.write(
            ModelTrainingDto("train", len(partitions.train.features), self._settings.model_type))
        validation = self.evaluate_model(model, partitions.validation)
        self._audit_service.write(MetricsDto("validation", validation))
        self._audit_service.write(ModelEvaluatedDto(
            "validation",
            len(partitions.validation.features),
            self._settings.model_type,
            validation,
        ))
        final = self.evaluate_model_with_predictions(model, partitions.test)
        self._audit_service.write(MetricsDto("test", final.metrics))
        self._audit_service.write(ModelEvaluatedDto(
            "test",
            len(partitions.test.features),
            self._settings.model_type,
            final.metrics,
        ))
        timestamp = datetime.now(timezone.utc)
        metadata = MetadataDto(
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
        self._audit_service.write(TrainedModelDto(model.pipeline))
        self._audit_service.write(ArtifactDto(model_path.with_suffix(".metadata.json"), ArtifactCategory.MODEL))
        self._audit_service.write(ModelSavedDto(model_path))
        result = ExperimentDto(
            run_id=run_id, timestamp=timestamp, dataset_name=self._settings.dataset_name,
            model_type=self._settings.model_type, model_parameters=metadata.model_parameters,
            validation_metrics=validation, test_metrics=final.metrics,
            model_path=model_path, audit_path=None,
            task_type=ExperimentTaskType.value_of(self._settings.task_type.value),
            model_selection_metric="f1_weighted" if self._search_enabled else None,
            model_selection_score=self._selected_model_score,
        )
        audit_data = TrainingAuditDto(
            experiment=result,
            model=model,
            evaluation=final,
            path=self._settings.audit_root,
            metrics={
                **{f"validation_{key}": float(value) for key, value in asdict(validation).items()},
                **{f"test_{key}": float(value) for key, value in asdict(final.metrics).items()},
            },
        )
        artifacts = self._visualization_facade.visualize(audit_data)
        self._audit_service.write(replace(audit_data, artifacts=artifacts))
        return result

    def download_dataset(self) -> tuple[pd.DataFrame, Path]:
        return self._dataset.download()

    def build_features_and_target(self, dataframe: pd.DataFrame) -> FeaturesAndTarget:
        dataframe = dataframe.dropna(subset=[self._settings.target_column]).copy()
        target = dataframe.pop(self._settings.target_column)
        return FeaturesAndTarget(FeatureBuilder(dataframe, self._feature_model).build(), target)

    def train_model(self, partitions: DatasetSplitDto) -> TrainedModel:
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
            key.removeprefix(f"{PipelineStep.CLASSIFIER}__"): value
            for key, value in selection.parameters.items()
        }
        self._selected_model_score = selection.f1_score
        return TrainedModel.from_pipeline(selection.pipeline)

    def evaluate_model(self, model, dto: FeaturesAndTarget) -> ClassificationMetrics:
        return self._evaluator.evaluate(
            dto.target, model.predict(dto.features)
        ).metrics

    def evaluate_model_with_predictions(self, model, dto: FeaturesAndTarget) -> EvaluationDto:
        y_true = dto.target
        y_pred = model.predict(dto.features)
        return self._evaluator.evaluate(y_true, y_pred)

    def save_model(self, model: TrainedModel, metadata: MetadataDto) -> Path:
        model_path = self._settings.model_root / self._settings.model_filename
        self._model_repository.save_model(model_path, model.pipeline, metadata)
        return model_path
