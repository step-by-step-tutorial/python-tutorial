from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from ml_prediction.audit.pipeline_step.pipeline_step_dto import PipelineStepDto


@dataclass(frozen=True)
class DatasetDownloadedDto(PipelineStepDto):
    dataset_path: Path
    step: ClassVar[str] = "dataset_downloaded"

    def to_dict(self) -> dict[str, Any]:
        return {"details": str(self.dataset_path)}
