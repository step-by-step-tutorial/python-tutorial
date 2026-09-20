from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from ml_prediction.audit.pipeline_step.pipeline_step_dto import PipelineStepDto


@dataclass(frozen=True)
class ExperimentCompletedDto(PipelineStepDto):
    audit_path: Path
    step: ClassVar[str] = "experiment_completed"

    def to_dict(self) -> dict[str, Any]:
        return {"details": str(self.audit_path)}
