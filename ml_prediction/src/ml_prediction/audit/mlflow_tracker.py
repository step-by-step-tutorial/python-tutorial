import logging
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

try:
    import mlflow
    import mlflow.sklearn
except ModuleNotFoundError:  # MLflow is optional for offline development.
    mlflow = None
try:
    from mlflow.exceptions import MlflowException
except ModuleNotFoundError:
    MlflowException = Exception

from ml_prediction.data_model.app_settings import AppSettings

logger = logging.getLogger(__name__)


class MlflowTracker:

    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings
        self._run = None
        self._enabled = False

    def start(self, experiment_id: str, parameters: dict[str, Any]) -> None:
        if not self._settings.mlflow_enabled or not self._settings.mlflow_tracking_uri:
            return
        if mlflow is None:
            if self._settings.mlflow_required:
                raise RuntimeError("MLflow is enabled but the mlflow package is not installed")
            logger.warning("MLflow package is unavailable; continuing with offline tracking")
            return
        mlflow.set_tracking_uri(self._settings.mlflow_tracking_uri)
        try:
            mlflow.set_experiment(
                f"{self._settings.mlflow_experiment_prefix}/{self._settings.dataset_name}"
            )
            self._run = mlflow.start_run(run_name=experiment_id)
            mlflow.set_tags({
                "dataset_name": self._settings.dataset_name,
                "task_type": self._settings.task_type.value,
                "model_type": self._settings.model_type,
            })
            mlflow.log_params(parameters)
            self._enabled = True
        except MlflowException:
            if self._settings.mlflow_required:
                raise
            logger.warning("MLflow is unavailable; continuing with offline tracking", exc_info=True)
            self._run = None

    def log_metrics(self, prefix: str, metrics: Any) -> None:
        if not self._enabled:
            return
        values = asdict(metrics) if is_dataclass(metrics) else metrics
        mlflow.log_metrics({f"{prefix}_{key}": float(value) for key, value in values.items()})

    def log_artifact(self, path: Path, artifact_path: str | None = None) -> None:
        if not self._enabled:
            return
        if path.exists():
            mlflow.log_artifact(str(path), artifact_path=artifact_path)

    def log_model(self, pipeline: Any) -> None:
        if not self._enabled:
            return
        mlflow.sklearn.log_model(
            pipeline,
            name="model",
            serialization_format="cloudpickle",
        )

    def end(self, status: str = "FINISHED") -> None:
        if self._enabled and self._run is not None:
            mlflow.end_run(status=status)
            self._run = None
            self._enabled = False
