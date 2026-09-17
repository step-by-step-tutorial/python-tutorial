from dataclasses import dataclass
from typing import Any, ClassVar

from ml_prediction.audit.pipeline_step.pipeline_step_data import PipelineStepData


@dataclass(frozen=True)
class FeaturesBuiltData(PipelineStepData):
    rows: int
    columns: int
    step: ClassVar[str] = "features_built"

    def to_dict(self) -> dict[str, Any]:
        return {"rows": self.rows, "details": f"columns={self.columns}"}
