from collections.abc import Callable
from pathlib import Path

import matplotlib.pyplot as plt

from ml_prediction.config.settings import get_settings
from ml_prediction.offline_tracking.experiment_reader import ExperimentReader
from ml_prediction.visualization.training_visualizer import TrainingVisualizer


class ExperimentVisualizer:

    def __init__(
            self,
            dataset_name: str,
    ) -> None:
        settings = get_settings(dataset_name)
        self.experiment_service = ExperimentReader(dataset_name)
        self.report_dir = settings.report_dir / "comparison"
        self.dataset_name = dataset_name

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
        experiments = self.experiment_service.read_all()
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
