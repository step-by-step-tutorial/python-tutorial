from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from ml_prediction.audit.pipeline_step.pipeline_step_data import PipelineStepData


@dataclass(frozen=True)
class ModelSavedData(PipelineStepData):
    model_path: Path
    step: ClassVar[str] = "model_saved"

    def to_dict(self) -> dict[str, Any]:
        return {"model_path": self.model_path, "details": str(self.model_path)}
