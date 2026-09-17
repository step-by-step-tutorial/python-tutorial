from typing import Any

from ml_prediction.data_model.metrics import Metrics


def create_metrics(values: dict[str, Any], metric_type: type[Metrics]) -> Metrics:
    return metric_type(**{key: float(value) for key, value in values.items()})
