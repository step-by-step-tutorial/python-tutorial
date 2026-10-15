from ml_platform.config.artifact_category import ArtifactCategory
from ml_platform.model.artifact_model import ArtifactModel
from ml_platform.model.settings_model import SettingsModel
from ml_platform.model.training_result_model import TrainingResultModel
from ml_platform.repository.experiment_repository import ExperimentRepository
from ml_platform.util.visualization_utils import save_line_chart
from ml_platform.visualize.visualizer import Visualizer

# (metric field, chart label, file name)
REGRESSION_COMPARISONS = (
    ("mean_absolute_error", "Validation MAE", "validation_mae.png"),
    ("root_mean_squared_error", "Validation RMSE", "validation_rmse.png"),
    ("r2_score", "Validation R2", "validation_r2.png"),
)


class ExperimentVisualizer(Visualizer):
    def __init__(self, settings: SettingsModel) -> None:
        self._settings = settings

    def render(self, result: TrainingResultModel) -> tuple[ArtifactModel, ...]:
        experiments = ExperimentRepository(self._settings.experiment_path).find_all()
        if not experiments:
            return ()

        labels = [f"{experiment.model_type}:{experiment.run_id[:8]}" for experiment in experiments]
        return tuple(
            ArtifactModel(
                save_line_chart(
                    labels=labels,
                    values=[getattr(experiment.validation_metrics, metric) for experiment in experiments],
                    path=self._settings.comparison_path(file_name),
                    x_label="Experiment",
                    y_label=label,
                    title=f"{label} by experiment",
                ),
                ArtifactCategory.PLOTS,
            )
            for metric, label, file_name in REGRESSION_COMPARISONS
        )
