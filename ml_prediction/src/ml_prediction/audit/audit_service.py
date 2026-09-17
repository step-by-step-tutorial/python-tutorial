from pathlib import Path
from ml_prediction.audit.data.audit_data import AuditData
from ml_prediction.audit.data.audit_operation import AuditOperation
from ml_prediction.utils.id_generator import IdGenerator
from ml_prediction.audit.experiment_service import ExperimentService
from ml_prediction.audit.mlflow_service import MlflowService
from ml_prediction.audit.audit_log_service import AuditLogService
from ml_prediction.audit.data_service import DataService
from ml_prediction.config.settings import get_settings
from ml_prediction.presentation.visualizer import Visualizer


class AuditService:
    def __init__(self, dataset_name: str) -> None:
        settings = get_settings(dataset_name)
        run_id = IdGenerator.generate()
        services: list[tuple[DataService, Path]] = [
            (AuditLogService(dataset_name, AuditOperation.TRAINING, run_id=run_id), settings.audit_path(AuditOperation.TRAINING, run_id)),
            (ExperimentService(), settings.experiment_path(run_id)),
            (Visualizer(dataset_name), settings.audit_path(AuditOperation.TRAINING, run_id))
        ]
        if settings.mlflow_enabled:
            services.append((MlflowService(settings), settings.audit_path(AuditOperation.TRAINING, run_id)))
        self._run_id = run_id
        self._services = services

    @property
    def run_id(self) -> str:
        return self._run_id

    def write(self, data: AuditData):
        for service, path in self._services:
            service.write(data, path)
