from dataclasses import dataclass
from typing import Any, ClassVar

from ml_prediction.audit.pipeline_step.pipeline_step_dto import PipelineStepDto


@dataclass(frozen=True)
class ModelTrainingDto(PipelineStepDto):
    partition: str
    rows: int
    model_name: str
    step: ClassVar[str] = "model_trained"

    def to_dict(self) -> dict[str, Any]:
        return {"partition": self.partition, "rows": self.rows, "model_name": self.model_name}
