import logging

from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from ml_prediction.data_model.classification_evaluation_data import ClassificationEvaluationData
from ml_prediction.data_model.classification_metrics import ClassificationMetrics

logger = logging.getLogger(__name__)


class ClassificationEvaluator:
    def evaluate(self, actual, predicted) -> ClassificationEvaluationData:
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
        return ClassificationEvaluationData(actual, predicted, metrics)
