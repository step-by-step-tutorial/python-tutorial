from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ml_prediction.audit.experiment import Experiment
from ml_prediction.audit.experiment_writer import ExperimentWriter
from ml_prediction.audit.mlflow_tracker import MlflowTracker
from ml_prediction.audit.report_event_data import ReportEventData
from ml_prediction.audit.report_writer import ReportWriter
from ml_prediction.config.settings import get_settings


class AuditService:
    """Coordinates durable audit output and external experiment tracking."""

    def __init__(self, dataset_name: str, mlflow_service: MlflowTracker | None = None,
                 experiment_writer: ExperimentWriter | None = None) -> None:
        settings = get_settings(dataset_name)
        self._report_dir = settings.report_dir
        self._experiment_writer = experiment_writer or ExperimentWriter(dataset_name)
        self._mlflow_service = mlflow_service or MlflowTracker(settings)
        self._report: ReportWriter | None = None

    @property
    def report_path(self) -> Path | None:
        return self._report.path if self._report is not None else None

    def start(self, dataset_name: str, operation: str, experiment_id: str, parameters: dict[str, Any]) -> None:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        path = self._report_dir / f"{dataset_name}_{operation}_report_{timestamp}.csv"
        self._report = ReportWriter(path, dataset_name, operation, run_id=experiment_id)
        self._mlflow_service.start(experiment_id, parameters)

    def record(self, event: ReportEventData) -> None:
        if self._report is None:
            raise RuntimeError("AuditService must be started before recording events")
        self._report.record(event)

    def log_metrics(self, prefix: str, metrics: Any) -> None:
        self._mlflow_service.log_metrics(prefix, metrics)

    def log_artifact(self, path: Path, category: str | None = None) -> None:
        self._mlflow_service.log_artifact(path, category)

    def log_model(self, pipeline: Any) -> None:
        self._mlflow_service.log_model(pipeline)

    def save_experiment(self, experiment: Experiment) -> None:
        self._experiment_writer.save(experiment)

    def finish(self, status: str = "FINISHED") -> None:
        self._mlflow_service.end(status)

    def __enter__(self) -> "AuditService":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.finish("FAILED" if exc_type is not None else "FINISHED")
