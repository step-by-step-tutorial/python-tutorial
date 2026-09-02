from pathlib import Path

from ml_prediction.data_model.app_settings import AppSettings
from ml_prediction.data_model.datalake_settings import DataLakeSettings
from ml_prediction.data_model.regression_metrics import RegressionMetrics
from ml_prediction.reporting.mlflow_tracker import MlflowTracker


def _settings() -> AppSettings:
    return AppSettings(
        data_dir=Path("data"),
        model_dir=Path("models"),
        target_column="target",
        validation_size=0.2,
        test_size=0.2,
        random_state=42,
        data_lake=DataLakeSettings("http://localhost", "key", "secret", "bucket", ""),
        dataset_name="house",
    )


def test_tracker_starts_dataset_experiment_and_logs_parameters(mocker) -> None:
    mlflow = mocker.patch("ml_prediction.reporting.mlflow_tracker.mlflow")
    tracker = MlflowTracker(_settings())

    tracker.start("experiment-1", {"n_estimators": 200})

    mlflow.set_tracking_uri.assert_called_once_with("sqlite:///./mlflow.db")
    mlflow.set_experiment.assert_called_once_with("ml_prediction/house")
    mlflow.start_run.assert_called_once_with(run_name="experiment-1")
    mlflow.log_params.assert_called_once_with({"n_estimators": 200})


def test_tracker_logs_dataclass_metrics_and_ends_run(mocker) -> None:
    mlflow = mocker.patch("ml_prediction.reporting.mlflow_tracker.mlflow")
    tracker = MlflowTracker(_settings())
    tracker.start("experiment-1", {})

    tracker.log_metrics("validation", RegressionMetrics(1.0, 2.0, 0.5))
    tracker.end()

    mlflow.log_metrics.assert_called_once_with({
        "validation_mean_absolute_error": 1.0,
        "validation_root_mean_squared_error": 2.0,
        "validation_r2_score": 0.5,
    })
    mlflow.end_run.assert_called_once_with(status="FINISHED")
