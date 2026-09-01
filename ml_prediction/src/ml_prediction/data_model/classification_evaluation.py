from dataclasses import dataclass
from typing import Any

from ml_prediction.data_model.classification_metrics import ClassificationMetrics


@dataclass(frozen=True)
class ClassificationEvaluation:
    y_true: Any
    y_pred: Any
    metrics: ClassificationMetrics
