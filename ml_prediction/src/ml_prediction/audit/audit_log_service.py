from datetime import datetime, timezone
from pathlib import Path

from ml_prediction.audit.data.audit_data import AuditData
from ml_prediction.audit.data.audit_operation import AuditOperation
from ml_prediction.audit.pipeline_step.pipeline_step_data import PipelineStepData
from ml_prediction.audit.data.audit_record import AuditRecord
from ml_prediction.audit.data_service import DataService
from ml_prediction.utils.csv_utils import read_csv, write_csv
from ml_prediction.utils.id_generator import IdGenerator


class AuditLogService(DataService):
    def __init__(self, dataset_name: str, operation: AuditOperation, run_id: str = "") -> None:
        self._dataset_name = dataset_name
        self._operation = operation
        self._run_id = run_id

    def read(self, path: Path) -> list[AuditRecord]:
        return read_csv(path, AuditRecord.from_dict)

    def write(self, data: AuditData, path: Path) -> AuditData | None:
        if not isinstance(data, PipelineStepData):
            return None
        fields = data.to_dict()
        selected_path = fields.get("model_path")
        metric_values = fields.get("metrics")
        audit_record = AuditRecord(
            datetime.now(timezone.utc),
            self._run_id,
            self._dataset_name,
            self._operation,
            data.step,
            fields.get("partition", ""),
            fields.get("rows"),
            fields.get("model_name", ""),
            str(selected_path or ""),
            IdGenerator.model_id(selected_path),
            metric_values,
            fields.get("details", ""),
        )
        write_csv(path, [audit_record])
        return data
