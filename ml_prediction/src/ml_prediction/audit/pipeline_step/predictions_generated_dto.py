from dataclasses import dataclass
from typing import Any, ClassVar

from ml_prediction.audit.pipeline_step.pipeline_step_dto import PipelineStepDto


@dataclass(frozen=True)
class PredictionsGeneratedDto(PipelineStepDto):
    rows: int
    feature_columns: int
    step: ClassVar[str] = "predictions_generated"

    def to_dict(self) -> dict[str, Any]:
        return {"rows": self.rows, "details": f"columns={self.feature_columns}"}
