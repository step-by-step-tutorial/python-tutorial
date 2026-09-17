from dataclasses import dataclass
from typing import Any, ClassVar

from ml_prediction.audit.pipeline_step.pipeline_step_data import PipelineStepData


@dataclass(frozen=True)
class DatasetSplitData(PipelineStepData):
    rows: int
    train_rows: int
    validation_rows: int
    test_rows: int
    step: ClassVar[str] = "dataset_split"

    def to_dict(self) -> dict[str, Any]:
        return {
            "rows": self.rows,
            "details": (
                f"train={self.train_rows} "
                f"validation={self.validation_rows} "
                f"test={self.test_rows}"
            ),
        }
