from datetime import datetime, timezone
from pathlib import Path

from ml_prediction.data_model.classification_metrics import ClassificationMetrics
from ml_prediction.data_model.regression_metrics import RegressionMetrics
from ml_prediction.audit.data.experiment_task_type import ExperimentTaskType
from ml_prediction.evaluation.experiment_comparison_service import ExperimentComparisonService
from ml_prediction.audit.data.experiment_dto import ExperimentDto
from ml_prediction.audit.data.training_audit_dto import TrainingAuditDto


def experiment(run_id: str, mae: float, rmse: float, r2: float) -> ExperimentDto:
    return ExperimentDto(
        run_id=run_id,
        timestamp=datetime.now(timezone.utc),
        dataset_name="house",
        task_type=ExperimentTaskType.REGRESSION,
        model_type="random_forest",
        model_parameters={},
        validation_metrics=RegressionMetrics(mae, rmse, r2),
        test_metrics=RegressionMetrics(12.0, 13.0, 0.2),
        model_path=Path(f"models/{run_id}.joblib"),
        audit_path=Path(f"reports/{run_id}.csv"),
    )


def classification_experiment(
        run_id: str,
        accuracy: float,
        precision: float,
        recall: float,
        f1_score: float,
) -> ExperimentDto:
    return ExperimentDto(
        run_id=run_id,
        timestamp=datetime.now(timezone.utc),
        dataset_name="online_shopping",
        model_type="random_forest",
        model_parameters={},
        task_type=ExperimentTaskType.CLASSIFICATION,
        validation_metrics=ClassificationMetrics(accuracy, precision, recall, f1_score),
        test_metrics=ClassificationMetrics(0.8, 0.8, 0.8, 0.8),
        model_path=Path(f"models/{run_id}.joblib"),
        audit_path=Path(f"reports/{run_id}.csv"),
    )


def test_comparison_service_returns_best_experiment_for_each_validation_metric(tmp_path: Path) -> None:
    service = ExperimentComparisonService("house")
    service.experiment_path = tmp_path / "experiments.csv"
    repository = service.repository
    experiments = [
        experiment("first", 3.0, 2.0, 0.7),
        experiment("second", 1.0, 4.0, 0.5),
        experiment("third", 2.0, 1.0, 0.9),
    ]
    for result in experiments:
        repository.write(TrainingAuditDto(experiment=result), service.experiment_path)

    assert service.best_by_validation_mae() == experiments[1]
    assert service.best_by_validation_rmse() == experiments[2]
    assert service.best_by_validation_r2() == experiments[2]
    assert repository.read(service.experiment_path) == experiments


def test_comparison_service_returns_none_for_empty_history(tmp_path: Path) -> None:
    service = ExperimentComparisonService("house")
    service.experiment_path = tmp_path / "experiments.csv"

    assert service.best_by_validation_mae() is None
    assert service.best_by_validation_rmse() is None
    assert service.best_by_validation_r2() is None


def test_comparison_service_returns_best_classification_experiment_for_each_validation_metric(
        tmp_path: Path,
) -> None:
    service = ExperimentComparisonService("online_shopping")
    service.experiment_path = tmp_path / "experiments.csv"
    repository = service.repository
    experiments = [
        classification_experiment("first", 0.80, 0.70, 0.90, 0.78),
        classification_experiment("second", 0.95, 0.85, 0.80, 0.82),
        classification_experiment("third", 0.88, 0.92, 0.86, 0.91),
    ]
    for result in experiments:
        repository.write(TrainingAuditDto(experiment=result), service.experiment_path)

    assert service.best_by_validation_accuracy() == experiments[1]
    assert service.best_by_validation_precision() == experiments[2]
    assert service.best_by_validation_recall() == experiments[0]
    assert service.best_by_validation_f1_score() == experiments[2]


