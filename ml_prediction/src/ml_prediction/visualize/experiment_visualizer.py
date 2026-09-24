from pathlib import Path

from ml_prediction.audit.data.artifact_category import ArtifactCategory
from ml_prediction.audit.data.artifact_dto import ArtifactDto
from ml_prediction.audit.data.training_audit_dto import TrainingAuditDto
from ml_prediction.audit.experiment_service import ExperimentService
from ml_prediction.config.settings import get_settings
from ml_prediction.data_model.regression_metrics import RegressionMetrics
from ml_prediction.visualize.visualizer import Visualizer
from ml_prediction.utils.visualization_utils import save_line_chart


class ExperimentVisualizer(Visualizer):

    def __init__(self, dataset_name: str):
        settings = get_settings(dataset_name)
        self._settings = settings
        self._experiment_service = ExperimentService()
        self._experiment_path = settings.audit_root / settings.experiment_filename
        self.audit_dir = settings.audit_root / settings.comparison_dirname
        self.dataset_name = dataset_name

    def render(self, dto: TrainingAuditDto) -> tuple[ArtifactDto, ...]:
        return tuple([
            ArtifactDto(self.save_validation_mae(), ArtifactCategory.PLOTS),
            ArtifactDto(self.save_validation_rmse(), ArtifactCategory.PLOTS),
            ArtifactDto(self.save_validation_r2(), ArtifactCategory.PLOTS),
        ])

    def save_validation_mae(self) -> Path | None:
        metric_data = self._read_metric_data("mean_absolute_error")
        if metric_data is None:
            return None
        labels, values = metric_data
        return save_line_chart(
            labels=labels,
            values=values,
            path=self.audit_dir / self._settings.validation_mae_filename,
            x_label="ExperimentDto",
            y_label="Validation MAE",
            title="Validation MAE by experiment",
        )

    def save_validation_rmse(self) -> Path | None:
        metric_data = self._read_metric_data("root_mean_squared_error")
        if metric_data is None:
            return None
        labels, values = metric_data
        return save_line_chart(
            labels=labels,
            values=values,
            path=self.audit_dir / self._settings.validation_rmse_filename,
            x_label="ExperimentDto",
            y_label="Validation RMSE",
            title="Validation RMSE by experiment",
        )

    def save_validation_r2(self) -> Path | None:
        metric_data = self._read_metric_data("r2_score")
        if metric_data is None:
            return None
        labels, values = metric_data
        return save_line_chart(
            labels=labels,
            values=values,
            path=self.audit_dir / self._settings.validation_r2_filename,
            x_label="ExperimentDto",
            y_label="Validation R2",
            title="Validation R2 by experiment",
        )

    def _read_metric_data(self, metric_name: str) -> tuple[tuple[str, ...], tuple[float, ...]] | None:
        experiments = self._experiment_service.read(self._experiment_path)
        if not experiments:
            return None
        return (
            tuple(f"{experiment.model_type}:{experiment.run_id[:8]}" for experiment in experiments),
            tuple(float(getattr(experiment.validation_metrics, metric_name)) for experiment in experiments),
        )
