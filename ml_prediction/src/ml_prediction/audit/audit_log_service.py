from datetime import datetime, timezone
from pathlib import Path

from ml_prediction.audit.data.audit_data import AuditData
from ml_prediction.audit.pipeline_step.pipeline_step_data import PipelineStepData
from ml_prediction.audit.data.audit_record import AuditRecord
from ml_prediction.audit.data_service import DataService
from ml_prediction.utils.csv_utils import read_csv, write_csv
from ml_prediction.utils.id_generator import IdGenerator


class AuditLogService(DataService):
    def __init__(self, dataset_name: str, operation: str, run_id: str = "") -> None:
        self.dataset = dataset_name
        self.operation = operation
        self._model_path: Path | None = None
        self.run_id = run_id

    def read(self, path: Path) -> list[AuditRecord]:
        return read_csv(path, AuditRecord.from_dict)

    def write(self, data: AuditData, path: Path) -> AuditData | None:
        if not isinstance(data, PipelineStepData):
            return None
        fields = data.to_dict()
        self._model_path = fields.get("model_path", self._model_path)
        selected_path = self._model_path
        metric_values = fields.get("metrics")
        audit_record = AuditRecord(
            datetime.now(timezone.utc), self.run_id, self.dataset, self.operation, data.step,
            fields.get("partition", ""), fields.get("rows"), fields.get("model_name", ""),
            str(selected_path or ""), IdGenerator.model_id(selected_path), metric_values,
            fields.get("details", ""),
        )
        write_csv(path, [audit_record])
        return data
