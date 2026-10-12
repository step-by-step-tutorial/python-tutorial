from dataclasses import dataclass
from typing import Any

from ml_prediction.config.task_type import TaskType
from ml_prediction.model.metrics_model import MetricsModel


@dataclass(frozen=True)
class EvaluationModel:
    actual: Any
    predicted: Any
    metrics: MetricsModel

    @classmethod
    def from_predictions(cls, task_type: TaskType, actual: Any, predicted: Any) -> "EvaluationModel":
        return cls(actual, predicted, MetricsModel.type_of(task_type).from_predictions(actual, predicted))
