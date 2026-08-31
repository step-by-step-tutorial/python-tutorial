import logging

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)

from ml_prediction.config.settings import TaskType
from ml_prediction.data_model.classification_metrics import ClassificationMetrics
from ml_prediction.data_model.evaluation_result import Evaluation
from ml_prediction.data_model.regression_metrics import RegressionMetrics

logger = logging.getLogger(__name__)


class ModelEvaluator:
    def __init__(self, task_type: TaskType = TaskType.REGRESSION) -> None:
        self._task_type = TaskType(task_type)

    def evaluate(self, actual, predicted) -> Evaluation:
        if self._task_type == TaskType.REGRESSION:
            metrics = RegressionMetrics(
                mean_absolute_error=float(mean_absolute_error(actual, predicted)),
                root_mean_squared_error=float(mean_squared_error(actual, predicted) ** 0.5),
                r2_score=float(r2_score(actual, predicted)),
            )
            logger.info(
                f"Model evaluation: "
                f"mae={metrics.mean_absolute_error} "
                f"rmse={metrics.root_mean_squared_error} "
                f"r2={metrics.r2_score}"
            )
        elif self._task_type == TaskType.CLASSIFICATION:
            metrics = ClassificationMetrics(
                accuracy=float(accuracy_score(actual, predicted)),
                precision=float(precision_score(actual, predicted, average="weighted", zero_division=0)),
                recall=float(recall_score(actual, predicted, average="weighted", zero_division=0)),
                f1_score=float(f1_score(actual, predicted, average="weighted", zero_division=0)),
            )

            logger.info(
                f"Model evaluation: "
                f"accuracy={metrics.accuracy} "
                f"precision={metrics.precision} "
                f"recall={metrics.recall} "
                f"f1={metrics.f1_score}"
            )
        else:
            raise Exception(f"Unknown task type: {self._task_type}")

        return Evaluation(actual, predicted, metrics)
