from pathlib import Path

from ml_prediction.audit.data.artifact_data import ArtifactData
from ml_prediction.config.settings import get_settings
from ml_prediction.audit.data.experiment_audit_data import ExperimentAuditData
from ml_prediction.data_model.evaluation_data import RegressionEvaluationData
from ml_prediction.presentation.presenter import Presenter
from ml_prediction.presentation.visual.artifact_visualizer import ArtifactVisualizer
from ml_prediction.presentation.visual.experiment_visualizer import ExperimentVisualizer


class VisualizationService(Presenter):
    def __init__(self, dataset_name: str) -> None:
        settings = get_settings(dataset_name)
        self._settings = settings
        self._artifact_visualizer = ArtifactVisualizer()
        self._experiment_visualizer = ExperimentVisualizer(dataset_name)

    def present(self, output: ExperimentAuditData) -> tuple[ArtifactData, ...]:
        if output.model is None or output.evaluation is None or output.experiment is None or output.audit_dir is None:
            return ()
        return self.publish(output.model, output.evaluation, output.experiment.run_id, output.audit_dir)

    def publish(self, model, evaluation, run_id: str, audit_dir: Path) -> tuple[ArtifactData, ...]:
        artifacts = []
        if isinstance(evaluation, RegressionEvaluationData):
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
                self._experiment_visualizer.save_validation_mae_comparison(),
                self._experiment_visualizer.save_validation_rmse_comparison(),
                self._experiment_visualizer.save_validation_r2_comparison(),
            ])
        artifact_dir = audit_dir / run_id
        artifacts.extend(artifact_dir.glob("*.png"))
        return tuple(ArtifactData(path, "plots") for path in {path for path in artifacts if isinstance(path, Path)})
