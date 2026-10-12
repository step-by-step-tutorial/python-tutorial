from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from ml_prediction.config.task_type import TaskType
from ml_prediction.model.metrics_model import MetricsModel

SCHEMA_VERSION = "1"
MODEL_VERSION = "1"


@dataclass(frozen=True)
class MetadataModel:
    run_id: str
    dataset_name: str
    task_type: TaskType
    model_type: str
    model_parameters: dict[str, Any]
    target_column: str
    prediction_column: str
    numeric_features: tuple[str, ...]
    boolean_features: tuple[str, ...]
    categorical_features: tuple[str, ...]
    training_timestamp: datetime
    validation_metrics: MetricsModel
    test_metrics: MetricsModel
    schema_version: str = SCHEMA_VERSION
    model_version: str = MODEL_VERSION

    @classmethod
    def from_dict(cls, values: dict[str, Any]) -> "MetadataModel":
        task_type = TaskType(values["task_type"])
        metrics_type = MetricsModel.type_of(task_type)
        return cls(**{
            **values,
            "task_type": task_type,
            "numeric_features": tuple(values["numeric_features"]),
            "boolean_features": tuple(values["boolean_features"]),
            "categorical_features": tuple(values["categorical_features"]),
            "training_timestamp": datetime.fromisoformat(values["training_timestamp"]),
            "validation_metrics": metrics_type.from_dict(values["validation_metrics"]),
            "test_metrics": metrics_type.from_dict(values["test_metrics"]),
        })

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "task_type": self.task_type.value,
            "training_timestamp": self.training_timestamp.isoformat(),
            "validation_metrics": self.validation_metrics.to_dict(),
            "test_metrics": self.test_metrics.to_dict(),
        }
