import logging

from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from ml_prediction.data_model.classification_metrics import ClassificationMetrics
from ml_prediction.data_model.evaluation_dto import EvaluationDto

logger = logging.getLogger(__name__)


class ClassificationEvaluator:
    def evaluate(self, actual, predicted) -> EvaluationDto:
        metrics = ClassificationMetrics(
            accuracy=float(accuracy_score(actual, predicted)),
            precision=float(precision_score(actual, predicted, average="weighted", zero_division=0)),
            recall=float(recall_score(actual, predicted, average="weighted", zero_division=0)),
            f1_score=float(f1_score(actual, predicted, average="weighted", zero_division=0)),
        )
        logger.info(
            f"Classification metrics: "
            f"accuracy={metrics.accuracy} "
            f"precision={metrics.precision} "
            f"recall={metrics.recall} "
            f"f1={metrics.f1_score}"
        )
        return EvaluationDto(actual, predicted, metrics)
