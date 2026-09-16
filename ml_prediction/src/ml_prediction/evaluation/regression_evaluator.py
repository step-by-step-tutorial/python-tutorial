import logging

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from ml_prediction.data_model.evaluation import RegressionEvaluation
from ml_prediction.data_model.regression_metrics import RegressionMetrics

logger = logging.getLogger(__name__)


class RegressionEvaluator:
    def evaluate(self, actual, predicted) -> RegressionEvaluation:
        metrics = RegressionMetrics(
            mean_absolute_error=float(mean_absolute_error(actual, predicted)),
            root_mean_squared_error=float(mean_squared_error(actual, predicted) ** 0.5),
            r2_score=float(r2_score(actual, predicted)),
        )
        logger.info(
            f"Regression metrics: "
            f"mae={metrics.mean_absolute_error} "
            f"rmse={metrics.root_mean_squared_error} "
            f"r2={metrics.r2_score}"
        )
        return RegressionEvaluation(actual, predicted, metrics)
