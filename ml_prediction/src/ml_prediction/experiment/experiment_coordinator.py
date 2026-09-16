from pathlib import Path
from uuid import uuid4

from ml_prediction.audit.audit_event import AuditEvent
from ml_prediction.audit.audit_service import AuditService
from ml_prediction.audit.experiment import Experiment
from ml_prediction.audit.experiment_completed import ExperimentCompleted
from ml_prediction.audit.experiment_reader import ExperimentReader
from ml_prediction.config.settings import get_settings
from ml_prediction.presentation.cli_experiment_presenter import CliExperimentPresenter
from ml_prediction.presentation.experiment_data import ExperimentData
from ml_prediction.presentation.visualization_service import VisualizationService


class ExperimentCoordinator:

    def __init__(self, dataset_name: str) -> None:
        self._settings = get_settings(dataset_name)
        self._audit = AuditService(dataset_name)
        visual_presenter = VisualizationService(dataset_name)
        self._presenters = (visual_presenter, CliExperimentPresenter())
        self._experiment_id: str | None = None
        self._data = ExperimentData()
        self._completed = False

    @property
    def report_path(self) -> Path | None:
        return self._audit.report_path

    @property
    def path(self) -> Path:
        return self._audit._experiment_writer.path

    @path.setter
    def path(self, value: Path) -> None:
        self._audit._experiment_writer.path = value

    def save(self, experiment: Experiment) -> None:
        self._audit.save_experiment(experiment)

    def read_all(self) -> list[Experiment]:
        reader = ExperimentReader(self._settings.dataset_name)
        reader.path = self.path
        return reader.read_all()

    def start(self, parameters: dict[str, object] | None = None) -> str:
        self._completed = False
        self._experiment_id = str(uuid4())
        self._audit.start(
            self._settings.dataset_name,
            "training",
            self._experiment_id,
            parameters or {},
        )
        return self._experiment_id

    def record(self, event: AuditEvent) -> None:
        self._audit.record(event)

    def log_metrics(self, prefix: str, metrics) -> None:
        self._audit.log_metrics(prefix, metrics)

    def log_artifact(self, path: Path, category: str | None = None) -> None:
        self._audit.log_artifact(path, category)

    def log_model(self, pipeline) -> None:
        self._audit.log_model(pipeline)

    def publish(self, data: ExperimentData) -> None:
        self._data = ExperimentData(
            experiment=data.experiment or self._data.experiment,
            model=data.model or self._data.model,
            evaluation=data.evaluation or self._data.evaluation,
            report_dir=data.report_dir or self._data.report_dir,
        )
        if data.experiment is not None:
            self._present(self._data)

    def complete(self, experiment: Experiment) -> None:
        if self._experiment_id is None:
            raise RuntimeError("ExperimentCoordinator must be started before completing")
        if self.report_path is not None:
            self._audit.record(ExperimentCompleted(self.report_path))
        self._audit.save_experiment(experiment)
        if self.report_path is not None:
            self._audit.log_artifact(self.report_path, "reports")
        self._data = ExperimentData(
            experiment=experiment,
            model=self._data.model,
            evaluation=self._data.evaluation,
            report_dir=self._data.report_dir,
        )
        self._present(self._data)
        self._audit.finish()
        self._completed = True

    def _present(self, data: ExperimentData) -> None:
        for presenter in self._presenters:
            presenter.present(data)

    def fail(self) -> None:
        self._audit.finish("FAILED")

    def __enter__(self) -> "ExperimentCoordinator":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type is not None:
            self.fail()
        elif not self._completed:
            self._audit.finish()
