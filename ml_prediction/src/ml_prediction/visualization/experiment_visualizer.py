from collections.abc import Callable
from pathlib import Path

from ml_prediction.reporting.experiment_repository import ExperimentRepository
from ml_prediction.visualization.training_visualizer import TrainingVisualizer

import matplotlib.pyplot as plt


class ExperimentVisualizer:
    """Creates separate comparison charts from persisted experiment history."""

    def __init__(self, experiment_repository: ExperimentRepository, report_dir: Path) -> None:
        self.experiment_repository = experiment_repository
        self.report_dir = report_dir

    def save_validation_mae_comparison(self) -> Path | None:
        return self._save_comparison(
            "validation_mae_comparison.png",
            "Validation MAE",
            lambda experiment: experiment.validation_metrics.mean_absolute_error,
        )

    def save_validation_rmse_comparison(self) -> Path | None:
        return self._save_comparison(
            "validation_rmse_comparison.png",
            "Validation RMSE",
            lambda experiment: experiment.validation_metrics.root_mean_squared_error,
        )

    def save_validation_r2_comparison(self) -> Path | None:
        return self._save_comparison(
            "validation_r2_comparison.png",
            "Validation R2",
            lambda experiment: experiment.validation_metrics.r2_score,
        )

    def _save_comparison(
            self,
            filename: str,
            metric_label: str,
            metric_value: Callable,
    ) -> Path | None:
        experiments = self.experiment_repository.read_all()
        if not experiments:
            return None

        labels = [f"{experiment.model_type}:{experiment.experiment_id[:8]}" for experiment in experiments]
        values = [metric_value(experiment) for experiment in experiments]
        figure, axes = plt.subplots()
        axes.plot(labels, values, marker="o")
        axes.set_xlabel("Experiment")
        axes.set_ylabel(metric_label)
        axes.set_title(f"{metric_label} by experiment")
        axes.tick_params(axis="x", labelrotation=45)
        figure.tight_layout()
        return TrainingVisualizer.save_figure(figure, self.report_dir / filename)
