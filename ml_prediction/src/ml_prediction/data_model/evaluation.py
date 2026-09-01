from dataclasses import dataclass
from typing import Any

from ml_prediction.data_model.regression_metrics import RegressionMetrics


@dataclass(frozen=True)
class RegressionEvaluation:
    y_true: Any
    y_pred: Any
    metrics: RegressionMetrics
