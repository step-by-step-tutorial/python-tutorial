from dataclasses import replace
from ml_prediction.audit.data.experiment_audit_data import ExperimentAuditData

from ml_prediction.audit.data.artifact_data import ArtifactData
from ml_prediction.audit.data.audit_data import AuditData
from ml_prediction.audit.data.experiment_data import ExperimentData
from ml_prediction.utils.id_generator import IdGenerator
from ml_prediction.audit.experiment_service import ExperimentService
from ml_prediction.audit.mlflow_service import MlflowService, mlflow
from ml_prediction.audit.pipeline_step.experiment_completed_data import ExperimentCompletedData
from ml_prediction.audit.audit_log_service import AuditLogService
from ml_prediction.audit.data_service import DataService
from ml_prediction.config.settings import get_settings
from ml_prediction.presentation.visualizer import Visualizer


class AuditService:
    def __init__(self, dataset_name: str) -> None:
        settings = get_settings(dataset_name)
        experiment_id = IdGenerator.generate()
        audit_path = settings.audit_path("training", experiment_id)
        audit_log_service = AuditLogService(dataset_name, "training", run_id=experiment_id)
        experiment_service = ExperimentService()
        tracking_configured = settings.mlflow_enabled and settings.mlflow_tracking_uri
        if tracking_configured and mlflow is None and settings.mlflow_required:
            raise RuntimeError("MLflow is enabled but the mlflow package is not installed")
        services: list[DataService] = [audit_log_service, experiment_service]
        if tracking_configured and mlflow is not None:
            services.append(MlflowService(settings))
        self._settings = settings
        self._experiment_id = experiment_id
        self._audit_path = audit_path
        self._experiment_path = settings.experiment_path(experiment_id)
        self._audit_log_service = audit_log_service
        self._experiment_service = experiment_service
        self._services = services
        self._services.insert(2, Visualizer(dataset_name))

    @property
    def experiment_id(self) -> str:
        return self._experiment_id

    def handle(self, data: AuditData) -> ExperimentData | None:
        if not isinstance(data, ExperimentAuditData):
            for service in self._services:
                self._write(service, data)
            return None

        audit_path = self._settings.audit_path("training", self.experiment_id)
        experiment = replace(data.experiment, audit_path=audit_path)
        completed_data = replace(
            data,
            experiment=experiment,
            artifacts=data.artifacts + (ArtifactData(audit_path, "audit"),),
        )
        for service in self._services:
            self._write(service, ExperimentCompletedData(audit_path))
            published_data = self._write(service, completed_data)
            if published_data is not None:
                completed_data = published_data
        return experiment

    def _write(self, service: DataService, data: AuditData):
        if service is self._audit_log_service:
            return service.write(data, self._audit_path)
        if service is self._experiment_service:
            return service.write(data, self._experiment_path)
        return service.write(data, self._audit_path)
