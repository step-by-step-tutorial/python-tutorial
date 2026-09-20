from dataclasses import asdict, dataclass
from typing import Any, ClassVar

from ml_prediction.audit.pipeline_step.pipeline_step_data import PipelineStepData
from ml_prediction.data_model.classification_metrics import ClassificationMetrics
from ml_prediction.data_model.regression_metrics import RegressionMetrics


@dataclass(frozen=True)
class ModelEvaluatedData(PipelineStepData):
    partition: str
    rows: int
    model_name: str
    metrics: RegressionMetrics | ClassificationMetrics
    step: ClassVar[str] = "model_evaluated"

    def to_dict(self) -> dict[str, Any]:
        return {
            "partition": self.partition,
            "rows": self.rows,
            "model_name": self.model_name,
            "metrics": asdict(self.metrics),
        }
