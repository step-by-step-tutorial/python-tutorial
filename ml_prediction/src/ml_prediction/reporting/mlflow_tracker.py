from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

import mlflow
import mlflow.sklearn

from ml_prediction.data_model.app_settings import AppSettings


class MlflowTracker:
    """Small MLflow adapter shared by the training implementations."""

    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings
        self._run = None

    def start(self, experiment_id: str, parameters: dict[str, Any]) -> None:
        mlflow.set_tracking_uri(self._settings.mlflow_tracking_uri)
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

    def log_metrics(self, prefix: str, metrics: Any) -> None:
        values = asdict(metrics) if is_dataclass(metrics) else metrics
        mlflow.log_metrics({f"{prefix}_{key}": float(value) for key, value in values.items()})

    @staticmethod
    def log_artifact(path: Path, artifact_path: str | None = None) -> None:
        if path.exists():
            mlflow.log_artifact(str(path), artifact_path=artifact_path)

    @staticmethod
    def log_model(pipeline: Any) -> None:
        mlflow.sklearn.log_model(
            pipeline,
            name="model",
            serialization_format="cloudpickle",
        )

    def end(self, status: str = "FINISHED") -> None:
        if self._run is not None:
            mlflow.end_run(status=status)
            self._run = None
