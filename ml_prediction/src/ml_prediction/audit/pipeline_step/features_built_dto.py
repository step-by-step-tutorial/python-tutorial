from dataclasses import dataclass
from typing import Any, ClassVar

from ml_prediction.audit.pipeline_step.pipeline_step_dto import PipelineStepDto


@dataclass(frozen=True)
class FeaturesBuiltDto(PipelineStepDto):
    rows: int
    columns: int
    step: ClassVar[str] = "features_built"

    def to_dict(self) -> dict[str, Any]:
        return {"rows": self.rows, "details": f"columns={self.columns}"}
