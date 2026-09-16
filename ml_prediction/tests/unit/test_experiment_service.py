from datetime import datetime, timezone
from pathlib import Path

from ml_prediction.data_model.datalake_settings import DataLakeSettings
from ml_prediction.data_model.regression_metrics import RegressionMetrics
from ml_prediction.data_model.app_settings import AppSettings
from ml_prediction.audit.experiment import Experiment
from ml_prediction.audit.experiment_completed import ExperimentCompleted
from ml_prediction.presentation.experiment_data import ExperimentData
from ml_prediction.experiment.experiment_service import ExperimentService
from ml_prediction.audit.audit_service import AuditService
from ml_prediction.audit.experiment_writer import ExperimentWriter
from ml_prediction.audit.mlflow_tracker import MlflowTracker
from ml_prediction.presentation.visual.artifact_visualizer import ArtifactVisualizer
from ml_prediction.presentation.visual.experiment_visualizer import ExperimentVisualizer
from ml_prediction.presentation.visualization_service import VisualizationService


def _settings(tmp_path: Path) -> AppSettings:
    return AppSettings(
        data_dir=tmp_path / "data",
        model_dir=tmp_path / "models",
        target_column="target",
        validation_size=0.2,
        test_size=0.2,
        random_state=42,
        data_lake=DataLakeSettings("http://localhost", "key", "secret", "bucket", ""),
        report_dir=tmp_path / "reports",
        dataset_name="house",
    )


def _experiment(tmp_path: Path) -> Experiment:
    metrics = RegressionMetrics(1.0, 2.0, 0.5)
    return Experiment(
        experiment_id="experiment-1",
        timestamp=datetime.now(timezone.utc),
        dataset_name="house",
        model_type="random_forest",
        model_parameters={},
        validation_metrics=metrics,
        test_metrics=metrics,
        model_path=tmp_path / "model.joblib",
        report_path=tmp_path / "report.csv",
    )


def test_experiment_service_delegates_completion_to_audit_and_presenters(tmp_path: Path, mocker) -> None:
    settings = _settings(tmp_path)
    mocker.patch("ml_prediction.experiment.experiment_service.get_settings", return_value=settings)
    audit = mocker.Mock()
    audit.report_path = tmp_path / "reports" / "experiment.csv"
    presenter = mocker.Mock()
    service = ExperimentService("house", audit_service=audit, presenters=(presenter,))
    service.start({"n_estimators": 10})
    data = ExperimentData(model=mocker.Mock(), evaluation=mocker.Mock(), report_dir=settings.report_dir)
    service.publish(data)
    experiment = _experiment(tmp_path)

    service.complete(experiment)

    audit.start.assert_called_once()
    audit.save_experiment.assert_called_once_with(experiment)
    audit.log_artifact.assert_called_once_with(audit.report_path, "reports")
    audit.record.assert_called_once()
    assert isinstance(audit.record.call_args.args[0], ExperimentCompleted)
    presenter.present.assert_called_once()
    assert presenter.present.call_args.args[0].experiment == experiment


def test_experiment_service_marks_failed_operations(tmp_path: Path, mocker) -> None:
    settings = _settings(tmp_path)
    mocker.patch("ml_prediction.experiment.experiment_service.get_settings", return_value=settings)
    audit = mocker.Mock()
    service = ExperimentService("house", audit_service=audit, presenters=())

    try:
        with service:
            raise ValueError("failed")
    except ValueError:
        pass

    audit.finish.assert_called_once_with("FAILED")


def test_audit_service_delegates_to_report_writer_and_tracker(tmp_path: Path, mocker) -> None:
    settings = _settings(tmp_path)
    mocker.patch("ml_prediction.audit.audit_service.get_settings", return_value=settings)
    report = mocker.Mock(path=tmp_path / "report.csv")
    report_writer = mocker.patch("ml_prediction.audit.audit_service.ReportWriter", return_value=report)
    writer = mocker.Mock(spec=ExperimentWriter)
    tracker = mocker.Mock(spec=MlflowTracker)
    service = AuditService("house", tracker, writer)

    service.start("house", "training", "experiment-1", {"depth": 4})
    event = mocker.Mock()
    service.record(event)
    service.log_metrics("test", {"score": 1.0})
    service.log_artifact(tmp_path / "plot.png", "plots")
    experiment = _experiment(tmp_path)
    service.save_experiment(experiment)
    service.finish("FINISHED")

    report_writer.assert_called_once()
    report.record.assert_called_once_with(event)
    tracker.start.assert_called_once_with("experiment-1", {"depth": 4})
    tracker.log_metrics.assert_called_once_with("test", {"score": 1.0})
    tracker.log_artifact.assert_called_once_with(tmp_path / "plot.png", "plots")
    writer.save.assert_called_once_with(experiment)
    tracker.end.assert_called_once_with("FINISHED")


def test_visualization_service_returns_logged_artifacts(tmp_path: Path, mocker) -> None:
    artifact_visualizer = mocker.Mock(spec=ArtifactVisualizer)
    artifact_visualizer.save_actual_vs_predicted.return_value = tmp_path / "actual.png"
    artifact_visualizer.save_residual_vs_predicted.return_value = tmp_path / "residual.png"
    artifact_visualizer.save_feature_importance.return_value = None
    experiment_visualizer = mocker.Mock(spec=ExperimentVisualizer)
    tracker = mocker.Mock()
    service = VisualizationService(artifact_visualizer, experiment_visualizer, tracker)
    evaluation = mocker.Mock()
    evaluation.metrics = mocker.Mock()

    artifacts = service.publish(mocker.Mock(), evaluation, "experiment-1", tmp_path)

    assert {artifact.path for artifact in artifacts} == {
        tmp_path / "actual.png", tmp_path / "residual.png",
    }
    assert all(artifact.category == "plots" for artifact in artifacts)


