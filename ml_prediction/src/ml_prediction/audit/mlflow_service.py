from pathlib import Path
from typing import Any

import mlflow
import mlflow.sklearn

from ml_prediction.audit.data.audit_data import AuditData
from ml_prediction.audit.data.experiment_audit_data import ExperimentAuditData
from ml_prediction.audit.data_service import DataService
from ml_prediction.data_model.app_settings import AppSettings


class MlflowService(DataService):
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        mlflow.set_experiment(f"{settings.mlflow_experiment_prefix}/{settings.dataset_name}")

    def read(self, path: Path) -> dict[str, Any]:
        return {}

    def write(self, data: AuditData, path: Path):
        if not isinstance(data, ExperimentAuditData) or data.experiment is None:
            return None

        mlflow.start_run(run_name=data.experiment.run_id)
        mlflow.set_tags({
            "dataset_name": self._settings.dataset_name,
            "task_type": self._settings.task_type.value,
            "model_type": self._settings.model_type,
        })
        mlflow.log_params(data.experiment.model_parameters)

        mlflow.log_metrics({key: float(value) for key, value in data.metrics.items()})
        mlflow.sklearn.log_model(data.model, name="model", serialization_format="cloudpickle")
        for artifact in data.artifacts:
            mlflow.log_artifact(str(artifact.path), artifact_path=artifact.category)

        mlflow.end_run(status="FINISHED")
