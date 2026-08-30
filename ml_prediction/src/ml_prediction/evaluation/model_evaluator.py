import logging
from dataclasses import dataclass
from typing import Any

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RegressionMetrics:
    mean_absolute_error: float
    root_mean_squared_error: float
    r2_score: float


@dataclass(frozen=True)
class EvaluationResult:
    y_true: Any
    y_pred: Any
    metrics: RegressionMetrics


class ModelEvaluator:
    def evaluate(self, actual, predicted) -> RegressionMetrics:
        return self.evaluate_with_predictions(actual, predicted).metrics

    def evaluate_with_predictions(self, actual, predicted) -> EvaluationResult:
        metrics = RegressionMetrics(
            mean_absolute_error=float(mean_absolute_error(actual, predicted)),
            root_mean_squared_error=float(mean_squared_error(actual, predicted) ** 0.5),
            r2_score=float(r2_score(actual, predicted)),
        )
        logger.info(
            f"Model evaluation: mae={metrics.mean_absolute_error:.2f} "
            f"rmse={metrics.root_mean_squared_error:.2f} "
            f"r2={metrics.r2_score:.4f}"
        )
        return EvaluationResult(actual, predicted, metrics)
