import pytest

from ml_platform.config.task_type import TaskType
from ml_platform.model.evaluation_model import EvaluationModel
from ml_platform.model.metrics_model import ClassificationMetricsModel, MetricsModel, RegressionMetricsModel


def test_regression_metrics_are_computed_from_predictions() -> None:
    metrics = RegressionMetricsModel.from_predictions([1.0, 2.0, 3.0], [1.0, 2.0, 5.0])

    assert metrics.mean_absolute_error == pytest.approx(2 / 3)
    assert metrics.root_mean_squared_error == pytest.approx((4 / 3) ** 0.5)
    assert metrics.to_string().startswith("mae=0.67 rmse=1.15")


def test_classification_metrics_are_computed_from_predictions() -> None:
    metrics = ClassificationMetricsModel.from_predictions(["a", "a", "b", "b"], ["a", "b", "b", "b"])

    assert metrics.accuracy == 0.75
    assert "accuracy=0.7500" in metrics.to_string()


@pytest.mark.parametrize("task_type, metrics_type", [
    (TaskType.REGRESSION, RegressionMetricsModel),
    (TaskType.CLASSIFICATION, ClassificationMetricsModel),
])
def test_metrics_type_follows_task_type(task_type, metrics_type) -> None:
    assert MetricsModel.type_of(task_type) is metrics_type


def test_metrics_round_trip_through_dict() -> None:
    metrics = RegressionMetricsModel(1.0, 2.0, 0.5)

    assert RegressionMetricsModel.from_dict(metrics.to_dict()) == metrics


def test_evaluation_keeps_actual_and_predicted_values() -> None:
    evaluation = EvaluationModel.from_predictions(TaskType.CLASSIFICATION, ["a"], ["a"])

    assert evaluation.actual == ["a"]
    assert evaluation.metrics.accuracy == 1.0
