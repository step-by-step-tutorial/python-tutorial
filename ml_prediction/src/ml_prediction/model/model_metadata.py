from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ml_prediction.evaluation.model_evaluator import EvaluationMetrics

CURRENT_SCHEMA_VERSION = "1"
CURRENT_MODEL_VERSION = "1"


@dataclass(frozen=True)
class ModelMetadata:
    model_type: str
    model_parameters: dict[str, Any]
    target_column: str
    numeric_features: tuple[str, ...]
    boolean_features: tuple[str, ...]
    categorical_features: tuple[str, ...]
    training_timestamp: datetime
    validation_metrics: EvaluationMetrics
    final_test_metrics: EvaluationMetrics
    schema_version: str
    model_version: str
    dataset_name: str = "house"
    task_type: str = "regression"
    prediction_column: str = "predicted_total_price"
