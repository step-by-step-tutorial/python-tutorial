import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd

from ml_prediction.config.settings import TaskType, get_settings
from ml_prediction.data_model.dataset_split import DatasetSplit
from ml_prediction.data_model.dataset_subset import DatasetSubset
from ml_prediction.data_model.evaluation import RegressionEvaluation
from ml_prediction.data_model.experiment import Experiment
from ml_prediction.data_model.features_and_target import FeaturesAndTarget
from ml_prediction.data_model.model_metadata import (
    CURRENT_MODEL_VERSION,
    CURRENT_SCHEMA_VERSION,
    ModelMetadata,
)
from ml_prediction.data_model.regression_metrics import RegressionMetrics
from ml_prediction.dataset.dataset import Dataset
from ml_prediction.evaluation.regression_evaluator import RegressionEvaluator
from ml_prediction.features.feature_builder import FeatureBuilder
from ml_prediction.features.house_feature_model import HouseFeatureModel
from ml_prediction.model.house_price_model import HousePriceModel
from ml_prediction.model_selection.regression_model_selector import RegressionModelSelector
from ml_prediction.pipeline.house_price_pipeline_builder import HousePricePipelineBuilder
from ml_prediction.pipeline.regressor_builder import RegressorBuilder
from ml_prediction.reporting.experiment_service import ExperimentService
from ml_prediction.reporting.mlflow_tracker import MlflowTracker
from ml_prediction.reporting.report_service import ReportService
from ml_prediction.repository.local_model_repository import LocalModelRepository
from ml_prediction.training.dataset_splitter import DatasetSplitter
from ml_prediction.training.trainer import Trainer
from ml_prediction.utils.data_validator_utils import should_be_same
from ml_prediction.visualization.experiment_visualizer import ExperimentVisualizer
from ml_prediction.visualization.training_visualizer import TrainingVisualizer

logger = logging.getLogger(__name__)


class HousePriceRegressionTrainer(Trainer[Experiment]):
    def __init__(self, dataset: Dataset, search_enabled: bool = False) -> None:
        self._settings = get_settings(dataset.dataset_name)
        self._dataset = dataset
        self._feature_model = HouseFeatureModel()
        self._report_service = ReportService(self._settings.report_dir)
        self._experiment_service = ExperimentService(dataset.dataset_name)
        self._mlflow_tracker = MlflowTracker(self._settings)
        self._training_visualizer = TrainingVisualizer()
        self._experiment_visualizer = ExperimentVisualizer(dataset.dataset_name)
        self._model_repository = LocalModelRepository()
        self._pipeline_builder = HousePricePipelineBuilder(self._feature_model, RegressorBuilder(dataset.dataset_name))
        self._evaluator = RegressionEvaluator()
        self._dataset_splitter = DatasetSplitter(dataset.dataset_name)
        self._search_enabled = search_enabled
        self._model_selector = RegressionModelSelector()
        self._selected_model_parameters: dict[str, object] | None = None
        self._selected_model_score: float | None = None

    def train(self) -> Experiment:
        should_be_same(
            first=self._settings.task_type,
            second=TaskType.REGRESSION,
            error_message=(
                f"HousePriceRegressionTrainer supports only regression tasks, "
                f"got '{self._settings.task_type}'"
            ),
        )

        report_events: list[tuple[str, dict[str, object]]] = []

        dataframe, dataset_path = self.download_dataset()
        features_and_target = self.build_features_and_target(dataframe)

        report_events.append((
            "dataset_downloaded",
            {
                "details": str(dataset_path)
            }
        ))
        report_events.append((
            "dataset_prepared",
            {
                "rows": len(features_and_target.features),
                "details": f"target={self._settings.target_column}",
            },
        ))
        report_events.append((
            "features_built",
            {
                "rows": len(features_and_target.features),
                "details": f"columns={len(features_and_target.features.columns)}",
            },
        ))
        report_events.append((
            "target_extracted",
            {
                "rows": len(features_and_target.target),
                "details": f"column={self._settings.target_column}",
            },
        ))

        dataset_subsets = self._dataset_splitter.split(features_and_target.features, features_and_target.target)

        report_events.append((
            "dataset_split",
            {
                "rows": len(features_and_target.features),
                "details": (
                    f"train={len(dataset_subsets.train.features)} "
                    f"validation={len(dataset_subsets.validation.features)} "
                    f"test={len(dataset_subsets.test.features)}"
                ),
            },
        ))

        experiment_id = str(uuid4())
        experiment_timestamp = datetime.now(timezone.utc)

        configured_parameters = {
            "n_estimators": self._settings.n_estimators,
            "n_jobs": self._settings.n_jobs,
            "max_depth": self._settings.max_depth,
            "min_samples_split": self._settings.min_samples_split,
            "min_samples_leaf": self._settings.min_samples_leaf,
            "max_features": self._settings.max_features,
            "bootstrap": self._settings.bootstrap,
            "random_state": self._settings.random_state,
        }

        logger.info(
            f"Starting training experiment: "
            f"experiment_id={experiment_id} "
            f"model_type={self._settings.model_type} "
            f"model_parameters={configured_parameters}",
        )
        self._mlflow_tracker.start(experiment_id, configured_parameters)
        self._mlflow_tracker.log_artifact(dataset_path, "dataset")

        logger.info(
            f"Evaluating model: "
            f"model={self._settings.model_type} "
            f"partition=validation rows={len(dataset_subsets.validation.features)}",
        )

        trained_model = self.train_model(dataset_subsets)

        report_events.append((
            "model_trained",
            {
                "partition": "train",
                "rows": len(dataset_subsets.train.features),
                "model_name": self._settings.model_type,
            },
        ))
        logger.info(
            f"Evaluating model: "
            f"model={self._settings.model_type} "
            f"partition=validation rows={len(dataset_subsets.validation.features)}",
        )

        validation_metrics = self.evaluate_model(trained_model, dataset_subsets.validation)
        self._mlflow_tracker.log_metrics("validation", validation_metrics)

        report_events.append((
            "model_evaluated",
            {
                "partition": "validation",
                "rows": len(dataset_subsets.validation.features),
                "model_name": self._settings.model_type,
                "metrics": validation_metrics,
            },
        ))

        logger.info(
            f"Evaluating model: "
            f"model={self._settings.model_type} "
            f"partition=test rows={len(dataset_subsets.test.features)}",
        )

        final_test_evaluation = self.evaluate_model_with_predictions(trained_model, dataset_subsets.test)
        final_test_metrics = final_test_evaluation.metrics
        self._mlflow_tracker.log_metrics("test", final_test_metrics)

        report_events.append((
            "model_evaluated",
            {
                "partition": "test",
                "rows": len(dataset_subsets.test.features),
                "model_name": self._settings.model_type,
                "metrics": final_test_metrics,
            },
        ))

        model_parameters = self._selected_model_parameters or configured_parameters
        metadata = ModelMetadata(
            model_type=self._settings.model_type,
            model_parameters=model_parameters,
            target_column=self._settings.target_column,
            numeric_features=self._feature_model.get_numeric_features(),
            boolean_features=self._feature_model.get_boolean_features(),
            categorical_features=self._feature_model.get_categorical_features(),
            training_timestamp=experiment_timestamp,
            validation_metrics=validation_metrics,
            final_test_metrics=final_test_metrics,
            schema_version=CURRENT_SCHEMA_VERSION,
            model_version=CURRENT_MODEL_VERSION,
            dataset_name=self._settings.dataset_name,
            task_type=self._settings.task_type.value,
            prediction_column=self._settings.prediction_column,
        )
        model_path = self.save_model(trained_model, metadata)
        self._mlflow_tracker.log_model(trained_model.pipeline)
        self._mlflow_tracker.log_artifact(model_path.with_suffix(".metadata.json"), "model")

        report = self._report_service.start(self._settings.dataset_name, "training", model_path)
        for step, details in report_events:
            report.record(step, **details)
        report.record("model_saved", model_path=model_path, details=str(model_path))
        report.record("training_completed", details=str(report.path))

        result = Experiment(
            experiment_id=experiment_id,
            timestamp=experiment_timestamp,
            dataset_name=self._settings.dataset_name,
            model_type=self._settings.model_type,
            model_parameters=metadata.model_parameters,
            validation_metrics=validation_metrics,
            test_metrics=final_test_metrics,
            model_path=model_path,
            report_path=report.path,
            model_selection_metric="mean_absolute_error" if self._search_enabled else None,
            model_selection_score=self._selected_model_score,
        )
        self._experiment_service.save(result)
        self._training_visualizer.save_actual_vs_predicted(
            final_test_evaluation.y_true,
            final_test_evaluation.y_pred,
            experiment_id,
            self._settings.report_dir,
        )
        self._training_visualizer.save_residual_vs_predicted(
            final_test_evaluation.y_true,
            final_test_evaluation.y_pred,
            experiment_id,
            self._settings.report_dir,
        )
        self._training_visualizer.save_feature_importance(
            trained_model,
            experiment_id,
            self._settings.report_dir,
        )
        self._mlflow_tracker.log_artifact(report.path, "reports")
        for artifact in (self._settings.report_dir / experiment_id).glob("*.png"):
            self._mlflow_tracker.log_artifact(artifact, "plots")
        self._experiment_visualizer.save_validation_mae_comparison()
        self._experiment_visualizer.save_validation_rmse_comparison()
        self._experiment_visualizer.save_validation_r2_comparison()
        self._mlflow_tracker.end()
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

    def train_model(self, partitions: DatasetSplit) -> HousePriceModel:
        if not self._search_enabled:
            return HousePriceModel(self._pipeline_builder).fit(partitions.train.features, partitions.train.target)

        pipeline = HousePriceModel(self._pipeline_builder).pipeline
        selection = self._model_selector.select(
            pipeline,
            partitions.train.features,
            partitions.train.target,
        )
        self._selected_model_parameters = {
            key.removeprefix("regressor__"): value
            for key, value in selection.parameters.items()
        }
        self._selected_model_score = selection.mean_absolute_error
        return HousePriceModel.from_pipeline(selection.pipeline)

    def evaluate_model(
            self,
            trained_model,
            dataset_partition: DatasetSubset
    ) -> RegressionMetrics:
        return self._evaluator.evaluate(
            dataset_partition.target,
            trained_model.predict(dataset_partition.features),
        ).metrics

    def evaluate_model_with_predictions(
            self,
            trained_model,
            dataset_partition: DatasetSubset,
    ) -> RegressionEvaluation:
        y_true = dataset_partition.target
        y_pred = trained_model.predict(dataset_partition.features)
        return self._evaluator.evaluate(y_true, y_pred)

    def save_model(self, trained_model: HousePriceModel, metadata: ModelMetadata) -> Path:
        return self._model_repository.save(
            trained_model.pipeline,
            self._settings.model_dir / self._settings.model_filename,
            metadata,
        )
