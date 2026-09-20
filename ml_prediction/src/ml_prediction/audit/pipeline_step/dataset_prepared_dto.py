from dataclasses import dataclass
from typing import Any, ClassVar

from ml_prediction.audit.pipeline_step.pipeline_step_dto import PipelineStepDto


@dataclass(frozen=True)
class DatasetPreparedDto(PipelineStepDto):
    rows: int
    target_column: str
    step: ClassVar[str] = "dataset_prepared"

    def to_dict(self) -> dict[str, Any]:
        return {"rows": self.rows, "details": f"target={self.target_column}"}
