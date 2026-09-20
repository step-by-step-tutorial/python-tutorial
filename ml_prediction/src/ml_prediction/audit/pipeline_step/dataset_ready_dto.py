from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from ml_prediction.audit.pipeline_step.pipeline_step_dto import PipelineStepDto


@dataclass(frozen=True)
class DatasetReadyDto(PipelineStepDto):
    dataset_path: Path
    step: ClassVar[str] = "dataset_ready"

    def to_dict(self) -> dict[str, Any]:
        return {"details": str(self.dataset_path)}
