from datetime import datetime, timezone
from pathlib import Path

from ml_prediction.evaluation.experiment_comparison_service import ExperimentComparisonService
from ml_prediction.data_model.experiment import Experiment
from ml_prediction.data_model.regression_metrics import RegressionMetrics
from ml_prediction.reporting.experiment_service import ExperimentService


def experiment(experiment_id: str, mae: float, rmse: float, r2: float) -> Experiment:
    return Experiment(
        experiment_id=experiment_id,
        timestamp=datetime.now(timezone.utc),
        dataset_name="house",
        model_type="random_forest",
        model_parameters={},
        validation_metrics=RegressionMetrics(mae, rmse, r2),
        test_metrics=RegressionMetrics(12.0, 13.0, 0.2),
        model_path=Path(f"models/{experiment_id}.joblib"),
        report_path=Path(f"reports/{experiment_id}.csv"),
    )


def test_comparison_service_returns_best_experiment_for_each_validation_metric(tmp_path: Path) -> None:
    service = ExperimentComparisonService("house")
    service.repository.path = tmp_path / "experiments.csv"
    repository = service.repository
    experiments = [
        experiment("first", 3.0, 2.0, 0.7),
        experiment("second", 1.0, 4.0, 0.5),
        experiment("third", 2.0, 1.0, 0.9),
    ]
    for result in experiments:
        repository.save(result)

    assert service.best_by_validation_mae() == experiments[1]
    assert service.best_by_validation_rmse() == experiments[2]
    assert service.best_by_validation_r2() == experiments[2]
    assert repository.read_all() == experiments


def test_comparison_service_returns_none_for_empty_history(tmp_path: Path) -> None:
    service = ExperimentComparisonService("house")
    service.repository.path = tmp_path / "experiments.csv"

    assert service.best_by_validation_mae() is None
    assert service.best_by_validation_rmse() is None
    assert service.best_by_validation_r2() is None
