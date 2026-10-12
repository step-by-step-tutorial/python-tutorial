import logging
from datetime import datetime, timezone

from sklearn.pipeline import Pipeline

from ml_prediction.audit.audit_service import AuditService
from ml_prediction.config.operation import Operation
from ml_prediction.estimator.model_selector import ModelSelector
from ml_prediction.estimator.pipeline_factory import create_estimator, create_pipeline
from ml_prediction.model.dataset_split_model import DatasetSplitModel, FeaturesAndTargetModel
from ml_prediction.model.evaluation_model import EvaluationModel
from ml_prediction.model.experiment_model import ExperimentModel
from ml_prediction.model.metadata_model import MetadataModel
from ml_prediction.model.selection_model import SelectionModel
from ml_prediction.model.settings_model import SettingsModel
from ml_prediction.model.training_result_model import TrainingResultModel
from ml_prediction.repository.dataset_repository import DatasetRepository
from ml_prediction.repository.model_repository import ModelRepository
from ml_prediction.visualize.visualizer_facade import VisualizerFacade

logger = logging.getLogger(__name__)


class Trainer:
    def __init__(self, settings: SettingsModel) -> None:
        self._settings = settings
        self._profile = settings.profile
        self._audit = AuditService(settings, Operation.TRAIN)
        self._dataset_repository = DatasetRepository(settings)
        self._model_repository = ModelRepository()
        self._model_selector = ModelSelector()
        self._visualizer = VisualizerFacade(settings)

    def train(self) -> TrainingResultModel:
        settings = self._settings
        logger.info("Training started: dataset=%s run_id=%s model_type=%s search=%s", settings.dataset_name,
                    self._audit.run_id, settings.model_type, settings.search_enabled)

        dataframe, dataset_path = self._dataset_repository.load()
        self._audit.log_step("dataset_loaded", rows=len(dataframe), details=str(dataset_path))

        data = FeaturesAndTargetModel.from_dataframe(dataframe, self._profile.target_column, self._profile.features)
        self._audit.log_step("features_built", rows=len(data), details=f"columns={len(data.features.columns)}")
        self._audit.log_step("target_extracted", rows=len(data), details=f"column={self._profile.target_column}")

        split = DatasetSplitModel.from_features(data, settings.validation_size, settings.test_size,
                                                settings.random_state)
        self._audit.log_step("dataset_split", rows=len(data), details=(
            f"train={len(split.train)} validation={len(split.validation)} test={len(split.test)}"
        ))

        pipeline, selection = self._fit(split.train)
        self._audit.log_step("model_trained", partition="train", rows=len(split.train),
                             model_name=settings.model_type)

        validation = self._evaluate(pipeline, split.validation, "validation")
        test = self._evaluate(pipeline, split.test, "test")

        experiment = ExperimentModel(
            run_id=self._audit.run_id,
            timestamp=datetime.now(timezone.utc),
            dataset_name=settings.dataset_name,
            task_type=settings.task_type,
            model_type=settings.model_type,
            model_parameters=selection.parameters if selection else settings.model_parameters.to_dict(),
            validation_metrics=validation.metrics,
            test_metrics=test.metrics,
            model_path=settings.model_path,
            selection_metric=selection.metric if selection else None,
            selection_score=selection.score if selection else None,
        )
        self._save_model(pipeline, experiment)
        self._audit.record_experiment(experiment)

        result = TrainingResultModel(experiment, pipeline, test)
        self._audit.publish(result, self._visualizer.render(result))
        logger.info("Training completed: dataset=%s run_id=%s validation[%s] test[%s] model=%s",
                    settings.dataset_name, experiment.run_id, validation.metrics.to_string(),
                    test.metrics.to_string(), experiment.model_path)
        return result

    def _fit(self, train: FeaturesAndTargetModel) -> tuple[Pipeline, SelectionModel | None]:
        settings = self._settings
        estimator = create_estimator(settings.task_type, settings.model_type, settings.model_parameters)
        pipeline = create_pipeline(self._profile.features, estimator)
        if settings.search_enabled:
            selection = self._model_selector.select(pipeline, train, settings.task_type, settings.model_type)
            return selection.pipeline, selection

        logger.info("Fitting model: model_type=%s rows=%s", settings.model_type, len(train))
        return pipeline.fit(train.features, train.target), None

    def _evaluate(self, pipeline: Pipeline, data: FeaturesAndTargetModel, partition: str) -> EvaluationModel:
        evaluation = EvaluationModel.from_predictions(self._settings.task_type, data.target,
                                                      pipeline.predict(data.features))
        logger.info("Evaluated model: partition=%s rows=%s %s", partition, len(data), evaluation.metrics.to_string())
        self._audit.log_step("model_evaluated", partition=partition, rows=len(data),
                             model_name=self._settings.model_type, metrics=evaluation.metrics)
        return evaluation

    def _save_model(self, pipeline: Pipeline, experiment: ExperimentModel) -> None:
        features = self._profile.features
        metadata = MetadataModel(
            run_id=experiment.run_id,
            dataset_name=experiment.dataset_name,
            task_type=experiment.task_type,
            model_type=experiment.model_type,
            model_parameters=experiment.model_parameters,
            target_column=self._profile.target_column,
            prediction_column=self._profile.prediction_column,
            numeric_features=features.numeric,
            boolean_features=features.boolean,
            categorical_features=features.categorical,
            training_timestamp=experiment.timestamp,
            validation_metrics=experiment.validation_metrics,
            test_metrics=experiment.test_metrics,
        )
        self._model_repository.save(experiment.model_path, pipeline, metadata)
        self._audit.log_step("model_saved", model_path=experiment.model_path, details=str(experiment.model_path))
