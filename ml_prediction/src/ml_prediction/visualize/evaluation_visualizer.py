from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
from sklearn.metrics import PredictionErrorDisplay

from ml_prediction.audit.data.artifact_category import ArtifactCategory
from ml_prediction.audit.data.artifact_dto import ArtifactDto
from ml_prediction.audit.data.training_audit_dto import TrainingAuditDto
from ml_prediction.config.settings import get_settings
from ml_prediction.visualize.visualizer import Visualizer


class EvaluationVisualizer(Visualizer):

    def __init__(self, dataset_name: str) -> None:
        self._settings = get_settings(dataset_name)

    def render(self, dto: TrainingAuditDto) -> tuple[ArtifactDto, ...]:
        if dto.model is None or dto.evaluation is None or dto.experiment is None:
            return ()

        run_id = dto.experiment.run_id
        y_true = dto.evaluation.y_true
        y_pred = dto.evaluation.y_pred

        actual_vs_predicted_path = self.save_actual_vs_predicted(y_true, y_pred, run_id)
        residual_vs_predicted_path = self.save_residual_vs_predicted(y_true, y_pred, run_id)

        return tuple([
                ArtifactDto(actual_vs_predicted_path, ArtifactCategory.PLOTS),
                ArtifactDto(residual_vs_predicted_path, ArtifactCategory.PLOTS),
            ])

    def save_actual_vs_predicted(self, y_true, y_pred, run_id: str) -> Path:
        path = self._settings.artifact_path(run_id, self._settings.actual_vs_predicted_filename)
        plot_type = "actual_vs_predicted"
        display = PredictionErrorDisplay.from_predictions(y_true, y_pred, kind=plot_type)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            display.figure_.savefig(path)
        finally:
            plt.close(display.figure_)
        return path

    def save_residual_vs_predicted(self, y_true, y_pred, run_id: str) -> Path:
        path = self._settings.artifact_path(run_id, self._settings.residual_vs_predicted_filename)
        plot_type = "residual_vs_predicted"
        display = PredictionErrorDisplay.from_predictions(np.asarray(y_true), np.asarray(y_pred), kind=plot_type)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            display.figure_.savefig(path)
        finally:
            plt.close(display.figure_)
        return path
