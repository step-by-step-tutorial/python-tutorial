from dataclasses import asdict, dataclass
from typing import Any, ClassVar

from ml_prediction.audit.pipeline_step.pipeline_step_dto import PipelineStepDto
from ml_prediction.data_model.metrics import Metrics


@dataclass(frozen=True)
class ModelEvaluatedDto(PipelineStepDto):
    partition: str
    rows: int
    model_name: str
    metrics: Metrics
    step: ClassVar[str] = "model_evaluated"

    def to_dict(self) -> dict[str, Any]:
        return {
            "partition": self.partition,
            "rows": self.rows,
            "model_name": self.model_name,
            "metrics": asdict(self.metrics),
        }
