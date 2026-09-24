from pathlib import Path

from ml_prediction.audit.data.audit_data import AuditData
from ml_prediction.audit.data.audit_operation import AuditOperation
from ml_prediction.audit.data.training_audit_dto import TrainingAuditDto
from ml_prediction.audit.data_service import DataService
from ml_prediction.audit.experiment_service import ExperimentService
from ml_prediction.audit.mlflow_service import MlflowService
from ml_prediction.audit.pipeline_audit_service import PipelineAuditService
from ml_prediction.audit.pipeline_step.pipeline_step_dto import PipelineStepDto
from ml_prediction.config.settings import get_settings
from ml_prediction.utils.id_generator import IdGenerator


class AuditService:
    def __init__(self, dataset_name: str) -> None:
        settings = get_settings(dataset_name)
        run_id = IdGenerator.generate()
        self._run_id = run_id
        self._services: dict[type[AuditData], list[tuple[DataService, Path]]] = {}
        if settings.execution_log_enabled:
            self._pipeline_audit_path = settings.audit_path(AuditOperation.TRAINING, run_id)
            self._pipeline_audit_service = PipelineAuditService(dataset_name, AuditOperation.TRAINING, run_id=run_id)
            self._services.setdefault(PipelineStepDto, []).append(
                (self._pipeline_audit_service, self._pipeline_audit_path))
        if settings.experiment_enabled:
            self._experiment_path = settings.experiment_path(run_id)
            self._experiment_service = ExperimentService()
            self._services.setdefault(TrainingAuditDto, []).append((self._experiment_service, self._experiment_path))
        if settings.mlflow_enabled:
            self._mlflow_path = settings.audit_path(AuditOperation.TRAINING, run_id)
            self._mlflow_service = MlflowService(settings)
            self._services.setdefault(TrainingAuditDto, []).append((self._mlflow_service, self._mlflow_path))

    @property
    def run_id(self) -> str:
        return self._run_id

    def write(self, dto: AuditData):
        for service, path in self._services.get(type(dto), []):
            service.write(dto, path)
        return
