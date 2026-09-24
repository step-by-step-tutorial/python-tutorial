from datetime import datetime, timezone
from dataclasses import replace
from ml_prediction.audit.data.training_audit_dto import TrainingAuditDto
from pathlib import Path

from ml_prediction.audit.data.experiment_dto import ExperimentDto
from ml_prediction.audit.data.artifact_dto import ArtifactDto
from ml_prediction.audit.data.artifact_category import ArtifactCategory
from ml_prediction.audit.data.experiment_task_type import ExperimentTaskType
from ml_prediction.audit.data.metrics_dto import MetricsDto
from ml_prediction.audit.data.trained_model_dto import TrainedModelDto
from ml_prediction.audit.pipeline_step.dataset_prepared_dto import DatasetPreparedDto
from ml_prediction.data_model.app_config import AppConfig
from ml_prediction.data_model.datalake_config import DataLakeconfig
from ml_prediction.data_model.regression_metrics import RegressionMetrics
from ml_prediction.data_model.evaluation_dto import EvaluationDto
from ml_prediction.audit.audit_service import AuditService
from ml_prediction.visualize.evaluation_visualizer import EvaluationVisualizer
from ml_prediction.visualize.experiment_visualizer import ExperimentVisualizer
from ml_prediction.visualize.model_interpretability_visualizer import ModelInterpretabilityVisualizer
from ml_prediction.visualize.visualizer_facade import VisualizationFacade


def _settings(tmp_path: Path) -> AppConfig:
    return AppConfig(
        data_root=tmp_path / "data", model_root=tmp_path / "models", target_column="target",
        validation_size=0.2, test_size=0.2, random_state=42,
        data_lake=DataLakeconfig("http://localhost", "key", "secret", "bucket", ""),
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
    mocker.patch("ml_prediction.audit.audit_service.PipelineAuditService", return_value=report)
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
    pipeline_audit_service = mocker.patch("ml_prediction.audit.audit_service.PipelineAuditService")

    AuditService("house")

    pipeline_audit_service.assert_not_called()


def test_visualization_service_returns_artifacts_without_tracking(tmp_path: Path, mocker) -> None:
    evaluation_visualizer = mocker.Mock(spec=EvaluationVisualizer)
    evaluation_visualizer.render.return_value = (
        ArtifactDto(tmp_path / "actual.png", ArtifactCategory.PLOTS),
        ArtifactDto(tmp_path / "residual.png", ArtifactCategory.PLOTS),
    )
    experiment_visualizer = mocker.Mock(spec=ExperimentVisualizer)
    experiment_visualizer.render.return_value = ()
    interpretability_visualizer = mocker.Mock(spec=ModelInterpretabilityVisualizer)
    interpretability_visualizer.render.return_value = ()
    mocker.patch("ml_prediction.visualize.visualizer_facade.EvaluationVisualizer", return_value=evaluation_visualizer)
    mocker.patch(
        "ml_prediction.visualize.visualizer_facade.ModelInterpretabilityVisualizer",
        return_value=interpretability_visualizer,
    )
    mocker.patch("ml_prediction.visualize.visualizer_facade.ExperimentVisualizer", return_value=experiment_visualizer)
    service = VisualizationFacade("house")
    evaluation = EvaluationDto([1.0], [1.0], RegressionMetrics(1.0, 2.0, 0.5))

    result = service.visualize(
        TrainingAuditDto(
            model=mocker.Mock(),
            evaluation=evaluation,
            experiment=mocker.Mock(run_id="experiment-1", task_type=ExperimentTaskType.REGRESSION),
        )
    )
    artifacts = result

    assert {artifact.path for artifact in artifacts} == {tmp_path / "actual.png", tmp_path / "residual.png"}
    assert all(artifact.category == "plots" for artifact in artifacts)
