from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from ml_prediction.audit.pipeline_step.pipeline_step_data import PipelineStepData


@dataclass(frozen=True)
class DatasetLoadedData(PipelineStepData):
    rows: int
    dataset_path: Path
    step: ClassVar[str] = "dataset_loaded"

    def to_dict(self) -> dict[str, Any]:
        return {"rows": self.rows, "details": str(self.dataset_path)}
