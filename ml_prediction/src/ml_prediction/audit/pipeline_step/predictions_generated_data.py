from dataclasses import dataclass
from typing import Any, ClassVar

from ml_prediction.audit.pipeline_step.pipeline_step_data import PipelineStepData


@dataclass(frozen=True)
class PredictionsGeneratedData(PipelineStepData):
    rows: int
    feature_columns: int
    step: ClassVar[str] = "predictions_generated"

    def to_dict(self) -> dict[str, Any]:
        return {"rows": self.rows, "details": f"columns={self.feature_columns}"}
