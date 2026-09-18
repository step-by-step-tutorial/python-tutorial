from ml_prediction.audit.data.audit_data import AuditData
from ml_prediction.audit.data.audit_operation import AuditOperation
from ml_prediction.audit.data.training_audit_data import TrainingAuditData
from ml_prediction.audit.execution_log_service_ import ExecutionLogService
from ml_prediction.audit.experiment_service import ExperimentService
from ml_prediction.audit.mlflow_service import MlflowService
from ml_prediction.audit.pipeline_step.pipeline_step_data import PipelineStepData
from ml_prediction.config.settings import get_settings
from ml_prediction.utils.id_generator import IdGenerator


class AuditService:
    def __init__(self, dataset_name: str) -> None:
        settings = get_settings(dataset_name)
        run_id = IdGenerator.generate()
        self._run_id = run_id
        self._execution_log_service = None
        self._experiment_service = None
        self._mlflow_service = None
        if settings.execution_log_enabled:
            self._execution_log_path = settings.audit_path(AuditOperation.TRAINING, run_id)
            self._execution_log_service = ExecutionLogService(dataset_name, AuditOperation.TRAINING, run_id=run_id)
        if settings.experiment_enabled:
            self._experiment_path = settings.experiment_path(run_id)
            self._experiment_service = ExperimentService()
        if settings.mlflow_enabled:
            self._mlflow_path = settings.audit_path(AuditOperation.TRAINING, run_id)
            self._mlflow_service = MlflowService(settings)

    @property
    def run_id(self) -> str:
        return self._run_id

    def write(self, data: AuditData):
        if isinstance(data, PipelineStepData) and self._execution_log_service is not None:
            self._execution_log_service.write(data, self._execution_log_path)
        elif isinstance(data, TrainingAuditData) and self._experiment_service is not None:
            self._experiment_service.write(data, self._experiment_path)
        elif isinstance(data, TrainingAuditData) and self._mlflow_service is not None:
            self._mlflow_service.write(data, self._mlflow_path)
        else:
            return
