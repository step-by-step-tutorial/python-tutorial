import csv
from datetime import datetime, timezone
import json
from pathlib import Path

from ml_prediction.data_model.experiment_result import Experiment
from ml_prediction.data_model.regression_metrics import RegressionMetrics
from ml_prediction.reporting.experiment_repository import ExperimentRepository


def test_experiment_repository_appends_and_reads_typed_results(tmp_path: Path) -> None:
    repository = ExperimentRepository()
    repository.path = tmp_path / "reports" / "experiments.csv"
    result = Experiment(
        experiment_id="experiment-1",
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        dataset_name="house",
        model_type="random_forest",
        model_parameters={"n_estimators": 200, "bootstrap": True},
        baseline_validation_metrics=RegressionMetrics(1.0, 2.0, 0.5),
        validation_metrics=RegressionMetrics(0.8, 1.5, 0.7),
        test_metrics=RegressionMetrics(0.9, 1.6, 0.65),
        model_path=tmp_path / "models" / "house.joblib",
        report_path=tmp_path / "reports" / "training.csv",
    )

    repository.save(result)
    repository.save(result)

    assert len(repository.read_all()) == 2
    assert repository.read_all()[0] == result
    assert len((tmp_path / "reports" / "experiments.csv").read_text().splitlines()) == 3
    with (tmp_path / "reports" / "experiments.csv").open(newline="") as history_file:
        rows = list(csv.DictReader(history_file))
    assert list(rows[0]) == list(ExperimentRepository.fieldnames)
    assert rows[0]["model_parameters"] == json.dumps(
        {"bootstrap": True, "n_estimators": 200},
        sort_keys=True,
        separators=(",", ":"),
    )
    assert rows[0]["baseline_validation_mae"] == "1.0"
    assert rows[0]["validation_rmse"] == "1.5"
    assert rows[0]["test_r2"] == "0.65"
