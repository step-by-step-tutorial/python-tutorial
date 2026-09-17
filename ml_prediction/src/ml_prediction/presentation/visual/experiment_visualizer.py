from collections.abc import Callable
from ml_prediction.audit.data.experiment_data import ExperimentData
from pathlib import Path

import matplotlib.pyplot as plt

from ml_prediction.audit.experiment_service import ExperimentService
from ml_prediction.config.settings import get_settings
from ml_prediction.presentation.visual.artifact_visualizer import ArtifactVisualizer


class ExperimentVisualizer:

    def __init__(
            self,
            dataset_name: str,
    ) -> None:
        settings = get_settings(dataset_name)
        self._settings = settings
        self._experiment_service = ExperimentService()
        self._experiment_path = settings.audit_dir / settings.experiment_filename
        self.audit_dir = settings.audit_dir / settings.comparison_dirname
        self.dataset_name = dataset_name

    def save_validation_mae_comparison(self) -> Path | None:
        return self._save_comparison(
            self._settings.validation_mae_filename,
            "Validation MAE",
            lambda experiment: experiment.validation_metrics.mean_absolute_error,
        )

    def save_validation_rmse_comparison(self) -> Path | None:
        return self._save_comparison(
            self._settings.validation_rmse_filename,
            "Validation RMSE",
            lambda experiment: experiment.validation_metrics.root_mean_squared_error,
        )

    def save_validation_r2_comparison(self) -> Path | None:
        return self._save_comparison(
            self._settings.validation_r2_filename,
            "Validation R2",
            lambda experiment: experiment.validation_metrics.r2_score,
        )

    def _save_comparison(
            self,
            filename: str,
            metric_label: str,
            metric_value: Callable,
    ) -> Path | None:
        experiments = self._experiment_service.read(self._experiment_path)
        if not experiments:
            return None

        labels = [f"{experiment.model_type}:{experiment.run_id[:8]}" for experiment in experiments]
        values = [metric_value(experiment) for experiment in experiments]
        figure, axes = plt.subplots()
        axes.plot(labels, values, marker="o")
        axes.set_xlabel("ExperimentData")
        axes.set_ylabel(metric_label)
        axes.set_title(f"{metric_label} by experiment")
        axes.tick_params(axis="x", labelrotation=45)
        figure.tight_layout()
        return ArtifactVisualizer.save_figure(figure, self.audit_dir / filename)
