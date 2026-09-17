from pathlib import Path
from ml_prediction.audit.data.experiment_audit_data import ExperimentAuditData
from datetime import datetime, timezone

from ml_prediction.audit.data.metrics_data import MetricsData
from ml_prediction.audit.data.trained_model_data import TrainedModelData
from ml_prediction.audit.data.experiment_data import ExperimentData
from ml_prediction.audit.mlflow_service import MlflowService
from ml_prediction.data_model.app_settings import AppSettings
from ml_prediction.data_model.datalake_settings import DataLakeSettings
from ml_prediction.data_model.regression_metrics import RegressionMetrics


def _settings() -> AppSettings:
    return AppSettings(
        data_dir=Path("data"), model_dir=Path("models"), target_column="target",
        validation_size=0.2, test_size=0.2, random_state=42,
        data_lake=DataLakeSettings("http://localhost", "key", "secret", "bucket", ""),
        dataset_name="house", mlflow_enabled=True, mlflow_tracking_uri="http://mlflow:5000",
    )


def test_tracker_publishes_parameters_and_metrics(mocker) -> None:
    mlflow = mocker.patch("ml_prediction.audit.mlflow_service.mlflow")
    mlflow_service = MlflowService(_settings())

    path = Path("audit.log")
    mlflow_service.write(MetricsData("validation", RegressionMetrics(1.0, 2.0, 0.5)), path)
    mlflow_service.write(TrainedModelData(mocker.Mock()), path)
    mlflow_service.write(ExperimentAuditData(experiment=ExperimentData(
        experiment_id="experiment-1", timestamp=datetime.now(timezone.utc),
        dataset_name="house", model_type="random_forest",
        model_parameters={"n_estimators": 200},
        validation_metrics=RegressionMetrics(1.0, 2.0, 0.5),
        test_metrics=RegressionMetrics(1.0, 2.0, 0.5),
        model_path=Path("model.joblib"), audit_path=Path("report.csv"),
    )), path)

    mlflow.set_tracking_uri.assert_called_once_with("http://mlflow:5000")
    mlflow.set_experiment.assert_called_once_with("ml_prediction/house")
    mlflow.start_run.assert_called_once_with(run_name="experiment-1")
    mlflow.log_params.assert_called_once_with({"n_estimators": 200})
    mlflow.log_metrics.assert_called_once_with({
        "validation_mean_absolute_error": 1.0,
        "validation_root_mean_squared_error": 2.0,
        "validation_r2_score": 0.5,
    })
    mlflow.end_run.assert_called_once_with(status="FINISHED")
