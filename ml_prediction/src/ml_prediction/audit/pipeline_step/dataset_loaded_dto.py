from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from ml_prediction.audit.pipeline_step.pipeline_step_dto import PipelineStepDto


@dataclass(frozen=True)
class DatasetLoadedDto(PipelineStepDto):
    rows: int
    dataset_path: Path
    step: ClassVar[str] = "dataset_loaded"

    def to_dict(self) -> dict[str, Any]:
        return {"rows": self.rows, "details": str(self.dataset_path)}
