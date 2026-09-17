from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from ml_prediction.audit.pipeline_step.pipeline_step_data import PipelineStepData


@dataclass(frozen=True)
class ExperimentCompletedData(PipelineStepData):
    audit_path: Path
    step: ClassVar[str] = "experiment_completed"

    def to_dict(self) -> dict[str, Any]:
        return {"details": str(self.audit_path)}
