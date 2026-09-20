from typing import Any

from ml_prediction.data_model.classification_metrics import ClassificationMetrics
from ml_prediction.data_model.regression_metrics import RegressionMetrics


def create_metrics(
    values: dict[str, Any],
    metric_type: type[RegressionMetrics | ClassificationMetrics],
) -> RegressionMetrics | ClassificationMetrics:
    return metric_type(**{key: float(value) for key, value in values.items()})
