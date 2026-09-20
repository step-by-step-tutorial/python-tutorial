from datetime import datetime, timezone
from dataclasses import replace
from ml_prediction.audit.data.training_audit_dto import TrainingAuditDto
from pathlib import Path

from ml_prediction.audit.data.experiment_dto import ExperimentDto
from ml_prediction.audit.data.artifact_dto import ArtifactDto
from ml_prediction.audit.data.artifact_category import ArtifactCategory
from ml_prediction.audit.data.metrics_dto import MetricsDto
from ml_prediction.audit.data.trained_model_dto import TrainedModelDto
from ml_prediction.audit.pipeline_step.dataset_prepared_dto import DatasetPreparedDto
from ml_prediction.data_model.app_settings import AppSettings
from ml_prediction.data_model.datalake_settings import DataLakeSettings
from ml_prediction.data_model.regression_metrics import RegressionMetrics
from ml_prediction.data_model.evaluation_dto import RegressionEvaluationDto
from ml_prediction.audit.audit_service import AuditService
from ml_prediction.presentation.visual.artifact_visualizer import ArtifactVisualizer
from ml_prediction.presentation.visual.experiment_visualizer import ExperimentVisualizer
from ml_prediction.presentation.visualization_view import VisualizationView


def _settings(tmp_path: Path) -> AppSettings:
    return AppSettings(
        data_root=tmp_path / "data", model_root=tmp_path / "models", target_column="target",
        validation_size=0.2, test_size=0.2, random_state=42,
        data_lake=DataLakeSettings("http://localhost", "key", "secret", "bucket", ""),
        audit_root=tmp_path / "reports", dataset_name="house",
        mlflow_enabled=True, mlflow_tracking_uri="http://mlflow:5000",
    )


def _experiment(tmp_path: Path) -> ExperimentDto:
    metrics = RegressionMetrics(1.0, 2.0, 0.5)
    return ExperimentDto(
        run_id="experiment-1", timestamp=datetime.now(timezone.utc),
        dataset_name="house", model_type="random_forest", model_parameters={},
        validation_metrics=metrics, test_metrics=metrics,
        model_path=tmp_path / "model.joblib", audit_path=None,
    )


def test_audit_service_writes_data_to_services(tmp_path: Path, mocker) -> None:
    settings = _settings(tmp_path)
    mocker.patch("ml_prediction.audit.audit_service.get_settings", return_value=settings)
    report = mocker.Mock()
    report.write.return_value = None
    writer = mocker.Mock()
    writer.write.return_value = None
    tracker = mocker.Mock()
    tracker.write.return_value = None
    mocker.patch("ml_prediction.audit.audit_service.ExecutionLogService", return_value=report)
    mocker.patch("ml_prediction.audit.audit_service.ExperimentService", return_value=writer)
    mocker.patch("ml_prediction.audit.audit_service.MlflowService", return_value=tracker)
    audit_service = AuditService("house")
    audit_service.write(MetricsDto("validation", RegressionMetrics(1.0, 2.0, 0.5)))
    audit_service.write(ArtifactDto(tmp_path / "dataset.csv", ArtifactCategory.DATASET))
    audit_service.write(TrainedModelDto(mocker.Mock()))
    audit_service.write(DatasetPreparedDto(10, "target"))

    dto = TrainingAuditDto(
        experiment=_experiment(tmp_path), model=mocker.Mock(), evaluation=mocker.Mock(),
        path=settings.audit_root,
    )
    audit_service.write(dto)

    assert any(call.args and isinstance(call.args[0], DatasetPreparedDto)
               for call in report.write.call_args_list)
    assert any(call.args and hasattr(call.args[0], "experiment")
               and call.args[0].experiment.run_id == dto.experiment.run_id
               for call in writer.write.call_args_list)


def test_audit_service_skips_execution_logging_when_disabled(tmp_path: Path, mocker) -> None:
    settings = replace(
        _settings(tmp_path),
        execution_log_enabled=False,
        experiment_enabled=False,
        mlflow_enabled=False,
    )
    mocker.patch("ml_prediction.audit.audit_service.get_settings", return_value=settings)
    execution_log_service = mocker.patch("ml_prediction.audit.audit_service.ExecutionLogService")

    AuditService("house")

    execution_log_service.assert_not_called()


def test_visualization_service_returns_artifacts_without_tracking(tmp_path: Path, mocker) -> None:
    artifact_visualizer = mocker.Mock(spec=ArtifactVisualizer)
    artifact_visualizer.save_actual_vs_predicted.return_value = tmp_path / "actual.png"
    artifact_visualizer.save_residual_vs_predicted.return_value = tmp_path / "residual.png"
    artifact_visualizer.save_feature_importance.return_value = None
    experiment_visualizer = mocker.Mock(spec=ExperimentVisualizer)
    mocker.patch("ml_prediction.presentation.visualization_view.ArtifactVisualizer", return_value=artifact_visualizer)
    mocker.patch("ml_prediction.presentation.visualization_view.ExperimentVisualizer", return_value=experiment_visualizer)
    service = VisualizationView("house")
    evaluation = RegressionEvaluationDto([1.0], [1.0], mocker.Mock())

    artifacts = service.publish(mocker.Mock(), evaluation, "experiment-1", tmp_path)

    assert {artifact.path for artifact in artifacts} == {tmp_path / "actual.png", tmp_path / "residual.png"}
    assert all(artifact.category == "plots" for artifact in artifacts)
