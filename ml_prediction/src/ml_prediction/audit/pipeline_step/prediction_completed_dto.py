from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from ml_prediction.audit.pipeline_step.pipeline_step_dto import PipelineStepDto


@dataclass(frozen=True)
class PredictionCompletedDto(PipelineStepDto):
    audit_path: Path
    step: ClassVar[str] = "prediction_completed"

    def to_dict(self) -> dict[str, Any]:
        return {"details": str(self.audit_path)}
