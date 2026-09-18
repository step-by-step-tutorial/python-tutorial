from datetime import datetime, timezone
from ml_prediction.audit.data.training_audit_data import TrainingAuditData
from pathlib import Path

from ml_prediction.data_model.classification_metrics import ClassificationMetrics
from ml_prediction.data_model.datalake_settings import DataLakeSettings
from ml_prediction.audit.experiment_service import ExperimentService
from ml_prediction.audit.data.experiment_data import ExperimentData
from ml_prediction.audit.data.experiment_task_type import ExperimentTaskType


def test_classification_experiment_round_trip(tmp_path: Path, mocker) -> None:
    experiment_path = tmp_path / "online_shopping_experiment_classification-1.csv"
    experiment = ExperimentData(
        run_id="classification-1",
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        dataset_name="online_shopping",
        task_type=ExperimentTaskType.CLASSIFICATION,
        model_type="random_forest",
        model_parameters={"n_estimators": 200},
        validation_metrics=ClassificationMetrics(0.9, 0.8, 0.7, 0.75),
        test_metrics=ClassificationMetrics(0.88, 0.79, 0.69, 0.74),
        model_path=tmp_path / "model.joblib",
        audit_path=tmp_path / "report.csv",
    )

    experiment_service = ExperimentService()
    experiment_service.write(TrainingAuditData(experiment=experiment), experiment_path)
    loaded = experiment_service.read(experiment_path)[0]

    assert loaded == experiment
    assert isinstance(loaded.validation_metrics, ClassificationMetrics)


