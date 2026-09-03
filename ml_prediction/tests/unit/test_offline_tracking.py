from datetime import datetime, timezone
from pathlib import Path

from ml_prediction.config.settings import get_settings
from ml_prediction.data_model.classification_metrics import ClassificationMetrics
from ml_prediction.data_model.datalake_settings import DataLakeSettings
from ml_prediction.offline_tracking.experiment_reader import ExperimentReader
from ml_prediction.offline_tracking.experiment_writer import ExperimentWriter
from ml_prediction.offline_tracking.models import Experiment


def test_classification_experiment_round_trip(tmp_path: Path, mocker) -> None:
    settings = mocker.patch("ml_prediction.offline_tracking.experiment_writer.get_settings")
    settings.return_value = mocker.Mock(report_dir=tmp_path, experiment_filename="experiments.csv")
    reader_settings = mocker.patch("ml_prediction.offline_tracking.experiment_reader.get_settings")
    reader_settings.return_value = settings.return_value
    experiment = Experiment(
        experiment_id="classification-1",
        run_id="run-1",
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        dataset_name="online_shopping",
        task_type="classification",
        model_type="random_forest",
        model_parameters={"n_estimators": 200},
        validation_metrics=ClassificationMetrics(0.9, 0.8, 0.7, 0.75),
        test_metrics=ClassificationMetrics(0.88, 0.79, 0.69, 0.74),
        model_path=tmp_path / "model.joblib",
        report_path=tmp_path / "report.csv",
    )

    ExperimentWriter("online_shopping").save(experiment)
    loaded = ExperimentReader("online_shopping").read_all()[0]

    assert loaded == experiment
    assert isinstance(loaded.validation_metrics, ClassificationMetrics)
