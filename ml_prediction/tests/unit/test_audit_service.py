from datetime import datetime, timezone
from ml_prediction.audit.data.experiment_audit_data import ExperimentAuditData
from pathlib import Path

from ml_prediction.audit.data.experiment_data import ExperimentData
from ml_prediction.audit.data.artifact_data import ArtifactData
from ml_prediction.audit.data.metrics_data import MetricsData
from ml_prediction.audit.data.trained_model_data import TrainedModelData
from ml_prediction.audit.pipeline_step.experiment_completed_data import ExperimentCompletedData
from ml_prediction.data_model.app_settings import AppSettings
from ml_prediction.data_model.datalake_settings import DataLakeSettings
from ml_prediction.data_model.regression_metrics import RegressionMetrics
from ml_prediction.audit.audit_service import AuditService
from ml_prediction.presentation.visual.artifact_visualizer import ArtifactVisualizer
from ml_prediction.presentation.visual.experiment_visualizer import ExperimentVisualizer
from ml_prediction.presentation.visualization_service import VisualizationService


def _settings(tmp_path: Path) -> AppSettings:
    return AppSettings(
        data_dir=tmp_path / "data", model_dir=tmp_path / "models", target_column="target",
        validation_size=0.2, test_size=0.2, random_state=42,
        data_lake=DataLakeSettings("http://localhost", "key", "secret", "bucket", ""),
        audit_dir=tmp_path / "reports", dataset_name="house",
        mlflow_enabled=True, mlflow_tracking_uri="http://mlflow:5000",
    )


def _experiment(tmp_path: Path) -> ExperimentData:
    metrics = RegressionMetrics(1.0, 2.0, 0.5)
    return ExperimentData(
        experiment_id="experiment-1", timestamp=datetime.now(timezone.utc),
        dataset_name="house", model_type="random_forest", model_parameters={},
        validation_metrics=metrics, test_metrics=metrics,
        model_path=tmp_path / "model.joblib", audit_path=None,
    )


def test_audit_service_publishes_completed_data_to_services_and_presenters(tmp_path: Path, mocker) -> None:
    settings = _settings(tmp_path)
    mocker.patch("ml_prediction.audit.audit_service.get_settings", return_value=settings)
    report = mocker.Mock()
    report.write.return_value = None
    writer = mocker.Mock()
    writer.write.return_value = None
    visual = mocker.Mock()
    visual.write.return_value = None
    tracker = mocker.Mock()
    tracker.write.return_value = None
    mocker.patch("ml_prediction.audit.audit_service.mlflow", mocker.Mock())
    mocker.patch("ml_prediction.audit.audit_service.AuditLogService", return_value=report)
    mocker.patch("ml_prediction.audit.audit_service.ExperimentService", return_value=writer)
    mocker.patch("ml_prediction.audit.audit_service.Visualizer", return_value=visual)
    mocker.patch("ml_prediction.audit.audit_service.MlflowService", return_value=tracker)
    audit_service = AuditService("house")
    audit_service.handle(MetricsData("validation", RegressionMetrics(1.0, 2.0, 0.5)))
    audit_service.handle(ArtifactData(tmp_path / "dataset.csv", "dataset"))
    audit_service.handle(TrainedModelData(mocker.Mock()))

    result = audit_service.handle(ExperimentAuditData(
        experiment=_experiment(tmp_path), model=mocker.Mock(), evaluation=mocker.Mock(),
        audit_dir=settings.audit_dir,
    ))

    assert result.audit_path == settings.audit_path("training", audit_service.experiment_id)
    assert any(call.args and isinstance(call.args[0], ExperimentCompletedData)
               for call in report.write.call_args_list)
    assert any(call.args and hasattr(call.args[0], "experiment")
               and call.args[0].experiment.experiment_id == result.experiment_id
               for call in writer.write.call_args_list)
    visual.write.assert_called()
    assert any(call.args and hasattr(call.args[0], "experiment")
               and call.args[0].experiment.experiment_id == result.experiment_id
               for call in tracker.write.call_args_list)


def test_visualization_service_returns_artifacts_without_tracking(tmp_path: Path, mocker) -> None:
    artifact_visualizer = mocker.Mock(spec=ArtifactVisualizer)
    artifact_visualizer.save_actual_vs_predicted.return_value = tmp_path / "actual.png"
    artifact_visualizer.save_residual_vs_predicted.return_value = tmp_path / "residual.png"
    artifact_visualizer.save_feature_importance.return_value = None
    experiment_visualizer = mocker.Mock(spec=ExperimentVisualizer)
    mocker.patch("ml_prediction.presentation.visualization_service.ArtifactVisualizer", return_value=artifact_visualizer)
    mocker.patch("ml_prediction.presentation.visualization_service.ExperimentVisualizer", return_value=experiment_visualizer)
    service = VisualizationService("house")
    evaluation = mocker.Mock()
    evaluation.metrics = mocker.Mock()

    artifacts = service.publish(mocker.Mock(), evaluation, "experiment-1", tmp_path)

    assert {artifact.path for artifact in artifacts} == {tmp_path / "actual.png", tmp_path / "residual.png"}
    assert all(artifact.category == "plots" for artifact in artifacts)
