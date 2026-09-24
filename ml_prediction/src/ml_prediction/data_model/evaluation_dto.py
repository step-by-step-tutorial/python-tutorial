from dataclasses import dataclass
from typing import Any

from ml_prediction.data_model.metrics import Metrics


@dataclass(frozen=True)
class EvaluationDto:
    y_true: Any
    y_pred: Any
    metrics: Metrics
