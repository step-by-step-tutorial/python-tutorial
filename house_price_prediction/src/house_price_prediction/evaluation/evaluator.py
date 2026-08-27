import logging
from dataclasses import dataclass

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RegressionMetrics:
    mean_absolute_error: float
    root_mean_squared_error: float
    r2_score: float


class ModelEvaluator:
    def evaluate(self, actual, predicted) -> RegressionMetrics:
        metrics = RegressionMetrics(
            mean_absolute_error=float(mean_absolute_error(actual, predicted)),
            root_mean_squared_error=float(mean_squared_error(actual, predicted) ** 0.5),
            r2_score=float(r2_score(actual, predicted)),
        )
        logger.info(
            "Model evaluation: mae=%.2f rmse=%.2f r2=%.4f",
            metrics.mean_absolute_error,
            metrics.root_mean_squared_error,
            metrics.r2_score,
        )
        return metrics
