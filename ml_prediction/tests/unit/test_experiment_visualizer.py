from datetime import datetime, timezone
from pathlib import Path

from ml_prediction.data_model.experiment_result import Experiment
from ml_prediction.data_model.regression_metrics import RegressionMetrics
from ml_prediction.reporting.experiment_repository import ExperimentRepository
from ml_prediction.visualization.experiment_visualizer import ExperimentVisualizer


def make_experiment(experiment_id: str, model_type: str) -> Experiment:
    return Experiment(
        experiment_id=experiment_id,
        timestamp=datetime.now(timezone.utc),
        dataset_name="house",
        model_type=model_type,
        model_parameters={},
        baseline_validation_metrics=RegressionMetrics(10.0, 11.0, 0.1),
        validation_metrics=RegressionMetrics(1.0, 2.0, 0.8),
        test_metrics=RegressionMetrics(3.0, 4.0, 0.5),
        model_path=Path(f"models/{experiment_id}.joblib"),
        report_path=Path(f"reports/{experiment_id}.csv"),
    )


def test_experiment_visualizer_creates_separate_metric_charts(tmp_path: Path) -> None:
    repository = ExperimentRepository()
    repository.path = tmp_path / "experiments.csv"
    repository.save(make_experiment("experiment-123456", "random_forest"))
    repository.save(make_experiment("experiment-abcdef", "extra_trees"))
    visualizer = ExperimentVisualizer(repository, tmp_path / "reports")

    mae_path = visualizer.save_validation_mae_comparison()
    rmse_path = visualizer.save_validation_rmse_comparison()
    r2_path = visualizer.save_validation_r2_comparison()

    assert mae_path == tmp_path / "reports" / "validation_mae_comparison.png"
    assert rmse_path == tmp_path / "reports" / "validation_rmse_comparison.png"
    assert r2_path == tmp_path / "reports" / "validation_r2_comparison.png"
    assert all(path.exists() for path in (mae_path, rmse_path, r2_path))


def test_experiment_visualizer_skips_empty_history(tmp_path: Path) -> None:
    repository = ExperimentRepository()
    repository.path = tmp_path / "experiments.csv"
    visualizer = ExperimentVisualizer(repository, tmp_path / "reports")

    assert visualizer.save_validation_mae_comparison() is None
    assert visualizer.save_validation_rmse_comparison() is None
    assert visualizer.save_validation_r2_comparison() is None
