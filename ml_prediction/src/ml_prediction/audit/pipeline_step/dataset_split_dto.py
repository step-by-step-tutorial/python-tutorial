from dataclasses import dataclass
from typing import Any, ClassVar

from ml_prediction.audit.pipeline_step.pipeline_step_dto import PipelineStepDto


@dataclass(frozen=True)
class DatasetSplitDto(PipelineStepDto):
    rows: int
    train_rows: int
    validation_rows: int
    test_rows: int
    step: ClassVar[str] = "dataset_split_dto"

    def to_dict(self) -> dict[str, Any]:
        return {
            "rows": self.rows,
            "details": (
                f"train={self.train_rows} "
                f"validation={self.validation_rows} "
                f"test={self.test_rows}"
            ),
        }
