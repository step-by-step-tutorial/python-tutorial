import logging
from dataclasses import dataclass
from typing import Any

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

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RegressionMetrics:
    mean_absolute_error: float
    root_mean_squared_error: float
    r2_score: float


@dataclass(frozen=True)
class ClassificationMetrics:
    accuracy: float
    precision: float
    recall: float
    f1_score: float


EvaluationMetrics = RegressionMetrics | ClassificationMetrics


@dataclass(frozen=True)
class EvaluationResult:
    y_true: Any
    y_pred: Any
    metrics: EvaluationMetrics


class ModelEvaluator:
    def __init__(self, task_type: TaskType = TaskType.REGRESSION) -> None:
        self._task_type = TaskType(task_type)

    def evaluate(self, actual, predicted) -> EvaluationMetrics:
        return self.evaluate_with_predictions(actual, predicted).metrics

    def evaluate_with_predictions(self, actual, predicted) -> EvaluationResult:
        if self._task_type == TaskType.REGRESSION:
            metrics = self._evaluate_regression(actual, predicted)
            logger.info(
                "Model evaluation: mae=%.2f rmse=%.2f r2=%.4f",
                metrics.mean_absolute_error,
                metrics.root_mean_squared_error,
                metrics.r2_score,
            )
        else:
            metrics = self._evaluate_classification(actual, predicted)
            logger.info(
                "Model evaluation: accuracy=%.4f precision=%.4f recall=%.4f f1=%.4f",
                metrics.accuracy,
                metrics.precision,
                metrics.recall,
                metrics.f1_score,
            )
        return EvaluationResult(actual, predicted, metrics)

    @staticmethod
    def _evaluate_regression(actual, predicted) -> RegressionMetrics:
        return RegressionMetrics(
            mean_absolute_error=float(mean_absolute_error(actual, predicted)),
            root_mean_squared_error=float(mean_squared_error(actual, predicted) ** 0.5),
            r2_score=float(r2_score(actual, predicted)),
        )

    @staticmethod
    def _evaluate_classification(actual, predicted) -> ClassificationMetrics:
        return ClassificationMetrics(
            accuracy=float(accuracy_score(actual, predicted)),
            precision=float(precision_score(actual, predicted, average="weighted", zero_division=0)),
            recall=float(recall_score(actual, predicted, average="weighted", zero_division=0)),
            f1_score=float(f1_score(actual, predicted, average="weighted", zero_division=0)),
        )
