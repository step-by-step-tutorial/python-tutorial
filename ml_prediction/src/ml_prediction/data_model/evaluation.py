from dataclasses import dataclass
from typing import Any

from ml_prediction.data_model.classification_metrics import ClassificationMetrics
from ml_prediction.data_model.regression_metrics import RegressionMetrics


@dataclass(frozen=True)
class Evaluation:
    y_true: Any
    y_pred: Any
    metrics: RegressionMetrics | ClassificationMetrics
