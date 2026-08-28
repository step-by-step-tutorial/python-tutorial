from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ml_prediction.evaluation.model_evaluator import RegressionMetrics


@dataclass(frozen=True)
class ModelMetadata:
    model_type: str
    model_parameters: dict[str, Any]
    target_column: str
    numeric_features: tuple[str, ...]
    boolean_features: tuple[str, ...]
    categorical_features: tuple[str, ...]
    training_timestamp: datetime
    validation_metrics: RegressionMetrics
    final_test_metrics: RegressionMetrics
    schema_version: str
    model_version: str
