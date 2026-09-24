from enum import Enum
from typing import Any

from ml_prediction.data_model.classification_metrics import ClassificationMetrics
from ml_prediction.data_model.regression_metrics import RegressionMetrics


class ExperimentTaskType(Enum):
    REGRESSION = ("regression", RegressionMetrics)
    CLASSIFICATION = ("classification", ClassificationMetrics)
    UNKNOWN = ("unknown", Any)

    metrics_type: Any

    def __new__(cls, value: str, metrics_type: Any) -> "ExperimentTaskType":
        member = object.__new__(cls)
        member._value_ = value
        member.metrics_type = metrics_type
        return member

    @classmethod
    def value_of(cls, value: str) -> "ExperimentTaskType":
        return cls(value)
