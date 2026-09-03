from pathlib import Path
from uuid import uuid4

from ml_prediction.data_model.app_settings import AppSettings
from ml_prediction.offline_tracking.experiment_writer import ExperimentWriter
from ml_prediction.offline_tracking.metadata_writer import MetadataWriter
from ml_prediction.offline_tracking.models import Experiment, ModelMetadata
from ml_prediction.offline_tracking.report_writer import ReportWriter


class OfflineRun:

    def __init__(self, settings: AppSettings, run_id: str, report: ReportWriter) -> None:
        self.run_id = run_id
        self.report = report
        self._experiment_writer = ExperimentWriter(settings.dataset_name)
        self._metadata_writer = MetadataWriter()

    @classmethod
    def start(cls, settings: AppSettings, operation: str, model_path: Path | None = None) -> "OfflineRun":
        run_id = str(uuid4())
        report_path = settings.report_dir / f"{settings.dataset_name}_{operation}_{run_id}.csv"
        report = ReportWriter(report_path, settings.dataset_name, operation, model_path, run_id)
        return cls(settings, run_id, report)

    def record(self, *args, **kwargs) -> None:
        self.report.record(*args, **kwargs)

    def save_metadata(self, metadata: ModelMetadata, model_path: Path) -> Path:
        return self._metadata_writer.save(metadata, model_path)

    def save_experiment(self, experiment: Experiment) -> None:
        self._experiment_writer.save(experiment)

    def finish(self) -> Path:
        self.record("run_completed", details=str(self.report.path))
        return self.report.path
