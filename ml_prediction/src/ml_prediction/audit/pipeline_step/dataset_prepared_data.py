from dataclasses import dataclass
from typing import Any, ClassVar

from ml_prediction.audit.pipeline_step.pipeline_step_data import PipelineStepData


@dataclass(frozen=True)
class DatasetPreparedData(PipelineStepData):
    rows: int
    target_column: str
    step: ClassVar[str] = "dataset_prepared"

    def to_dict(self) -> dict[str, Any]:
        return {"rows": self.rows, "details": f"target={self.target_column}"}
