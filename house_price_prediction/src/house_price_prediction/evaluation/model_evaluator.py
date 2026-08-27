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
    def __init__(self, actual, predicted) -> None:
        self.actual = actual
        self.predicted = predicted

    def evaluate(self) -> RegressionMetrics:
        metrics = RegressionMetrics(
            mean_absolute_error=float(mean_absolute_error(self.actual, self.predicted)),
            root_mean_squared_error=float(mean_squared_error(self.actual, self.predicted) ** 0.5),
            r2_score=float(r2_score(self.actual, self.predicted)),
        )
        logger.info(
            f"Model evaluation: mae={metrics.mean_absolute_error:.2f} "
            f"rmse={metrics.root_mean_squared_error:.2f} "
            f"r2={metrics.r2_score:.4f}"
        )
        return metrics
