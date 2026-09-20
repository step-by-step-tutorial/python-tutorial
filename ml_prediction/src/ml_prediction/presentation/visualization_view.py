from pathlib import Path

from ml_prediction.audit.data.artifact_category import ArtifactCategory
from ml_prediction.audit.data.artifact_dto import ArtifactDto
from ml_prediction.audit.data.training_audit_dto import TrainingAuditDto
from ml_prediction.config.settings import get_settings
from ml_prediction.data_model.evaluation_dto import RegressionEvaluationDto
from ml_prediction.presentation.view import View
from ml_prediction.presentation.visual.artifact_visualizer import ArtifactVisualizer
from ml_prediction.presentation.visual.experiment_visualizer import ExperimentVisualizer


class VisualizationView(View):
    def __init__(self, dataset_name: str) -> None:
        settings = get_settings(dataset_name)
        self._settings = settings
        self._artifact_visualizer = ArtifactVisualizer()
        self._experiment_visualizer = ExperimentVisualizer(dataset_name)

    def render(self, dto: TrainingAuditDto) -> tuple[ArtifactDto, ...]:
        if dto.model is None or dto.evaluation is None or dto.experiment is None or dto.path is None:
            return ()
        return self.publish(dto.model, dto.evaluation, dto.experiment.run_id, dto.path)

    def publish(self, model, evaluation, run_id: str, audit_dir: Path) -> tuple[ArtifactDto, ...]:
        artifacts = []
        if isinstance(evaluation, RegressionEvaluationDto):
            artifacts.extend([
                self._artifact_visualizer.save_actual_vs_predicted(
                    evaluation.y_true, evaluation.y_pred, run_id, audit_dir,
                    self._settings.artifact_path(run_id, self._settings.actual_vs_predicted_filename),
                ),
                self._artifact_visualizer.save_residual_vs_predicted(
                    evaluation.y_true, evaluation.y_pred, run_id, audit_dir,
                    self._settings.artifact_path(run_id, self._settings.residual_vs_predicted_filename),
                ),
            ])
        artifacts.append(self._artifact_visualizer.save_feature_importance(
            model, run_id, audit_dir,
            output_path=self._settings.artifact_path(
                run_id, self._settings.feature_importance_filename,
            ),
        ))
        if hasattr(evaluation.metrics, "mean_absolute_error"):
            artifacts.extend([
                self._experiment_visualizer.save_validation_mae(),
                self._experiment_visualizer.save_validation_rmse(),
                self._experiment_visualizer.save_validation_r2(),
            ])
        artifact_dir = audit_dir / run_id
        artifacts.extend(artifact_dir.glob("*.png"))
        return tuple(ArtifactDto(path, ArtifactCategory.PLOTS) for path in
                     {path for path in artifacts if isinstance(path, Path)})
