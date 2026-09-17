from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

try:
    import mlflow
    import mlflow.sklearn
except ModuleNotFoundError:
    mlflow = None

from ml_prediction.audit.data.artifact_data import ArtifactData
from ml_prediction.audit.data.audit_data import AuditData
from ml_prediction.audit.data.metrics_data import MetricsData
from ml_prediction.audit.data.trained_model_data import TrainedModelData
from ml_prediction.data_model.app_settings import AppSettings
from ml_prediction.audit.data.experiment_audit_data import ExperimentAuditData
from ml_prediction.audit.data_service import DataService


class MlflowService(DataService):
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings
        self._metrics: list[tuple[str, Any]] = []
        self._artifacts: list[tuple[Path, str | None]] = []
        self._model: Any = None

    def read(self, path: Path) -> dict[str, Any]:
        return {
            "metrics": tuple(self._metrics),
            "artifacts": tuple(self._artifacts),
            "model": self._model,
        }

    def write(self, data: AuditData, path: Path) -> AuditData | None:
        if isinstance(data, MetricsData):
            self._metrics.append((data.prefix, data.metrics))
            return
        if isinstance(data, ArtifactData):
            self._artifacts.append((data.path, data.category))
            return
        if isinstance(data, TrainedModelData):
            self._model = data.model
            return
        if not isinstance(data, ExperimentAuditData):
            return

        mlflow.set_tracking_uri(self._settings.mlflow_tracking_uri)
        mlflow.set_experiment(
            f"{self._settings.mlflow_experiment_prefix}/{self._settings.dataset_name}"
        )
        mlflow.start_run(run_name=data.experiment.experiment_id)
        mlflow.set_tags({
            "dataset_name": self._settings.dataset_name,
            "task_type": self._settings.task_type.value,
            "model_type": self._settings.model_type,
        })
        mlflow.log_params(data.experiment.model_parameters)

        try:
            for prefix, values in self._metrics:
                self._write_metrics(prefix, values)
            for artifact in self._artifacts + [
                (item.path, item.category) for item in data.artifacts
            ]:
                self._write_artifact(*artifact)
            self._write_model(self._model)
        except Exception:
            mlflow.end_run(status="FAILED")
            raise
        else:
            mlflow.end_run(status="FINISHED")

    @staticmethod
    def _write_metrics(prefix: str, metrics: Any) -> None:
        values = asdict(metrics) if is_dataclass(metrics) else metrics
        mlflow.log_metrics({f"{prefix}_{key}": float(value) for key, value in values.items()})

    @staticmethod
    def _write_artifact(path: Path, category: str | None) -> None:
        mlflow.log_artifact(str(path), artifact_path=category)

    @staticmethod
    def _write_model(model: Any) -> None:
        mlflow.sklearn.log_model(model, name="model", serialization_format="cloudpickle")
