from dataclasses import dataclass
from typing import Any, ClassVar

from ml_prediction.audit.pipeline_step.pipeline_step_dto import PipelineStepDto


@dataclass(frozen=True)
class TargetExtractedDto(PipelineStepDto):
    rows: int
    target_column: str
    step: ClassVar[str] = "target_extracted"

    def to_dict(self) -> dict[str, Any]:
        return {"rows": self.rows, "details": f"column={self.target_column}"}
