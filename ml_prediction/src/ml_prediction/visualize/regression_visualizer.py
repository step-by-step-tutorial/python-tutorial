import logging
from pathlib import Path

import numpy as np
from sklearn.metrics import PredictionErrorDisplay
from sklearn.pipeline import Pipeline

from ml_prediction.config.artifact_category import ArtifactCategory
from ml_prediction.config.pipeline_step import PipelineStep
from ml_prediction.model.artifact_model import ArtifactModel
from ml_prediction.model.settings_model import SettingsModel
from ml_prediction.model.training_result_model import TrainingResultModel
from ml_prediction.util.visualization_utils import save_figure, save_horizontal_bar_chart
from ml_prediction.visualize.visualizer import Visualizer

logger = logging.getLogger(__name__)

TOP_FEATURE_COUNT = 20


class RegressionVisualizer(Visualizer):
    def __init__(self, settings: SettingsModel) -> None:
        self._settings = settings

    def render(self, result: TrainingResultModel) -> tuple[ArtifactModel, ...]:
        run_id = result.experiment.run_id
        actual = np.asarray(result.test_evaluation.actual)
        predicted = np.asarray(result.test_evaluation.predicted)
        paths = [
            self._save_prediction_error(actual, predicted, "actual_vs_predicted", run_id),
            self._save_prediction_error(actual, predicted, "residual_vs_predicted", run_id),
            self._save_feature_importance(result.pipeline, run_id),
        ]
        return tuple(ArtifactModel(path, ArtifactCategory.PLOTS) for path in paths if path is not None)

    def _save_prediction_error(self, actual: np.ndarray, predicted: np.ndarray, kind: str, run_id: str) -> Path:
        display = PredictionErrorDisplay.from_predictions(actual, predicted, kind=kind)
        return save_figure(display.figure_, self._settings.artifact_path(run_id, f"{kind}.png"))

    def _save_feature_importance(self, pipeline: Pipeline, run_id: str) -> Path | None:
        importances = getattr(pipeline.named_steps[PipelineStep.ESTIMATOR], "feature_importances_", None)
        if importances is None:
            logger.info("Skipped feature importance: model_type=%s has no feature importances",
                        self._settings.model_type)
            return None

        feature_names = pipeline.named_steps[PipelineStep.PREPROCESSOR].get_feature_names_out()
        order = np.argsort(importances)[::-1][:TOP_FEATURE_COUNT]
        return save_horizontal_bar_chart(
            labels=feature_names[order],
            values=importances[order],
            path=self._settings.artifact_path(run_id, "feature_importance.png"),
            x_label="Importance",
            y_label="Feature",
            title="Feature importance",
        )
