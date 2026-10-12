import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from ml_prediction.audit.mlflow_service import MlflowService
from ml_prediction.config.operation import Operation
from ml_prediction.model.artifact_model import ArtifactModel
from ml_prediction.model.execution_model import ExecutionModel
from ml_prediction.model.experiment_model import ExperimentModel
from ml_prediction.model.metrics_model import MetricsModel
from ml_prediction.model.settings_model import SettingsModel
from ml_prediction.model.training_result_model import TrainingResultModel
from ml_prediction.repository.experiment_repository import ExperimentRepository
from ml_prediction.util.csv_utils import append_rows
from ml_prediction.util.file_utils import sha256

logger = logging.getLogger(__name__)


class AuditService:
    def __init__(self, settings: SettingsModel, operation: Operation) -> None:
        self._settings = settings
        self._operation = operation
        self.run_id = str(uuid4())
        self.execution_log_path = settings.execution_log_path(operation, self.run_id)

    def log_step(
            self,
            step: str,
            *,
            partition: str = "",
            rows: int | None = None,
            model_name: str = "",
            model_path: Path | None = None,
            metrics: MetricsModel | None = None,
            details: str = "",
    ) -> None:
        if not self._settings.execution_log_enabled:
            return
        execution = ExecutionModel(
            timestamp=datetime.now(timezone.utc),
            run_id=self.run_id,
            dataset_name=self._settings.dataset_name,
            operation=self._operation,
            step=step,
            partition=partition,
            rows=rows,
            model_name=model_name,
            model_path=str(model_path or ""),
            model_id=sha256(model_path) if model_path else "",
            metrics=metrics.to_dict() if metrics else {},
            details=details,
        )
        append_rows(self.execution_log_path, [execution.to_dict()])

    def record_experiment(self, experiment: ExperimentModel) -> None:
        if self._settings.experiment_enabled:
            ExperimentRepository(self._settings.experiment_path).append(experiment)

    def publish(self, result: TrainingResultModel, artifacts: tuple[ArtifactModel, ...]) -> None:
        if self._settings.mlflow.enabled:
            MlflowService(self._settings).publish(result, artifacts)
            logger.info("Published experiment to MLflow: run_id=%s", self.run_id)
