from pathlib import Path

from ml_prediction.audit.artifact_data import ArtifactData
from ml_prediction.audit.mlflow_tracker import MlflowTracker
from ml_prediction.presentation.experiment_data import ExperimentData
from ml_prediction.presentation.presenter import Presenter
from ml_prediction.presentation.visual.artifact_visualizer import ArtifactVisualizer
from ml_prediction.presentation.visual.experiment_visualizer import ExperimentVisualizer


class VisualizationService(Presenter):
    def __init__(
            self,
            artifact_visualizer: ArtifactVisualizer,
            experiment_visualizer: ExperimentVisualizer,
            tracker: MlflowTracker,
    ) -> None:
        self._artifact_visualizer = artifact_visualizer
        self._experiment_visualizer = experiment_visualizer
        self._tracker = tracker

    def present(self, data: ExperimentData) -> tuple[ArtifactData, ...]:
        if data.model is None or data.evaluation is None or data.experiment is None or data.report_dir is None:
            return ()
        return self.publish(data.model, data.evaluation, data.experiment.experiment_id, data.report_dir)

    def publish(self, model, evaluation, experiment_id: str, report_dir: Path) -> tuple[ArtifactData, ...]:
        artifacts = [
            self._artifact_visualizer.save_actual_vs_predicted(
                evaluation.y_true, evaluation.y_pred, experiment_id, report_dir,
            ),
            self._artifact_visualizer.save_residual_vs_predicted(
                evaluation.y_true, evaluation.y_pred, experiment_id, report_dir,
            ),
            self._artifact_visualizer.save_feature_importance(model, experiment_id, report_dir),
        ]
        if hasattr(evaluation.metrics, "mean_absolute_error"):
            artifacts.extend([
                self._experiment_visualizer.save_validation_mae_comparison(),
                self._experiment_visualizer.save_validation_rmse_comparison(),
                self._experiment_visualizer.save_validation_r2_comparison(),
            ])
        artifact_dir = report_dir / experiment_id
        artifacts.extend(artifact_dir.glob("*.png"))
        for artifact in {path for path in artifacts if isinstance(path, Path)}:
            self._tracker.log_artifact(artifact, "plots")
        return tuple(ArtifactData(path, "plots") for path in {path for path in artifacts if isinstance(path, Path)})
