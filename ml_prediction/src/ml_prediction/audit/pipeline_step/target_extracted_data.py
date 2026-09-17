from dataclasses import dataclass
from typing import Any, ClassVar

from ml_prediction.audit.pipeline_step.pipeline_step_data import PipelineStepData


@dataclass(frozen=True)
class TargetExtractedData(PipelineStepData):
    rows: int
    target_column: str
    step: ClassVar[str] = "target_extracted"

    def to_dict(self) -> dict[str, Any]:
        return {"rows": self.rows, "details": f"column={self.target_column}"}
