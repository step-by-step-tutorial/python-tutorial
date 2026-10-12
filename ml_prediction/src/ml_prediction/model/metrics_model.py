from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any, Self

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)

from ml_prediction.config.task_type import TaskType


class MetricsModel(ABC):

    @staticmethod
    def type_of(task_type: TaskType) -> type["MetricsModel"]:
        return {
            TaskType.REGRESSION: RegressionMetricsModel,
            TaskType.CLASSIFICATION: ClassificationMetricsModel,
        }[task_type]

    @classmethod
    @abstractmethod
    def from_predictions(cls, actual: Any, predicted: Any) -> Self:
        ...

    @classmethod
    def from_dict(cls, values: Mapping[str, Any]) -> Self:
        return cls(**{key: float(value) for key, value in values.items()})

    def to_dict(self) -> dict[str, float]:
        return {key: float(value) for key, value in asdict(self).items()}

    @abstractmethod
    def to_string(self) -> str:
        ...


@dataclass(frozen=True)
class RegressionMetricsModel(MetricsModel):
    mean_absolute_error: float
    root_mean_squared_error: float
    r2_score: float

    @classmethod
    def from_predictions(cls, actual: Any, predicted: Any) -> "RegressionMetricsModel":
        return cls(
            mean_absolute_error=float(mean_absolute_error(actual, predicted)),
            root_mean_squared_error=float(mean_squared_error(actual, predicted) ** 0.5),
            r2_score=float(r2_score(actual, predicted)),
        )

    def to_string(self) -> str:
        return f"mae={self.mean_absolute_error:.2f} rmse={self.root_mean_squared_error:.2f} r2={self.r2_score:.4f}"


@dataclass(frozen=True)
class ClassificationMetricsModel(MetricsModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float

    @classmethod
    def from_predictions(cls, actual: Any, predicted: Any) -> "ClassificationMetricsModel":
        return cls(
            accuracy=float(accuracy_score(actual, predicted)),
            precision=float(precision_score(actual, predicted, average="weighted", zero_division=0)),
            recall=float(recall_score(actual, predicted, average="weighted", zero_division=0)),
            f1_score=float(f1_score(actual, predicted, average="weighted", zero_division=0)),
        )

    def to_string(self) -> str:
        return (
            f"accuracy={self.accuracy:.4f} precision={self.precision:.4f} "
            f"recall={self.recall:.4f} f1={self.f1_score:.4f}"
        )
