from datetime import datetime, timezone
from pathlib import Path

from ml_prediction.audit.data.audit_operation import AuditOperation
from ml_prediction.audit.data.execution_dto import ExecutionDto
from ml_prediction.audit.data_service import DataService
from ml_prediction.audit.pipeline_step.pipeline_step_dto import PipelineStepDto
from ml_prediction.utils.csv_utils import read_csv, write_csv
from ml_prediction.utils.id_generator import IdGenerator


class ExecutionLogService(DataService):
    def __init__(self, dataset_name: str, operation: AuditOperation, run_id: str = "") -> None:
        self._dataset_name = dataset_name
        self._operation = operation
        self._run_id = run_id

    def read(self, path: Path) -> list[ExecutionDto]:
        return read_csv(path, ExecutionDto.from_dict)

    def write(self, dto: PipelineStepDto, path: Path) -> None:
        fields = dto.to_dict()
        selected_path = fields.get("model_path")
        metric_values = fields.get("metrics")
        execution_dto = ExecutionDto(
            datetime.now(timezone.utc),
            self._run_id,
            self._dataset_name,
            self._operation,
            dto.step,
            fields.get("partition", ""),
            fields.get("rows"),
            fields.get("model_name", ""),
            str(selected_path or ""),
            IdGenerator.model_id(selected_path),
            metric_values,
            fields.get("details", ""),
        )
        write_csv(path, [execution_dto])
