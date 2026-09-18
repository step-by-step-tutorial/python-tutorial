from datetime import datetime, timezone
from ml_prediction.audit.data.training_audit_data import TrainingAuditData
from pathlib import Path

from ml_prediction.audit.data.experiment_data import ExperimentData
from ml_prediction.audit.experiment_service import ExperimentService
from ml_prediction.data_model.regression_metrics import RegressionMetrics
from ml_prediction.presentation.visual.experiment_visualizer import ExperimentVisualizer


def make_experiment(run_id: str, model_type: str) -> ExperimentData:
    return ExperimentData(
        run_id=run_id,
        timestamp=datetime.now(timezone.utc),
        dataset_name="house",
        model_type=model_type,
        model_parameters={},
        validation_metrics=RegressionMetrics(1.0, 2.0, 0.8),
        test_metrics=RegressionMetrics(3.0, 4.0, 0.5),
        model_path=Path(f"models/{run_id}.joblib"),
        audit_path=Path(f"reports/{run_id}.csv"),
    )


def test_experiment_visualizer_creates_separate_metric_charts(tmp_path: Path, mocker) -> None:
    mocker.patch(
        "ml_prediction.presentation.visual.experiment_visualizer.get_settings",
        return_value=mocker.Mock(
            audit_dir=tmp_path / "reports",
            experiment_filename="experiments.csv",
            comparison_dirname="comparison",
            validation_mae_filename="validation_mae_comparison.png",
            validation_rmse_filename="validation_rmse_comparison.png",
            validation_r2_filename="validation_r2_comparison.png",
        ),
    )
    visualizer = ExperimentVisualizer("house")
    experiment_path = tmp_path / "experiments.csv"
    visualizer._experiment_path = experiment_path
    writer = ExperimentService()
    writer.write(TrainingAuditData(experiment=make_experiment("experiment-123456", "random_forest")), experiment_path)
    writer.write(TrainingAuditData(experiment=make_experiment("experiment-abcdef", "extra_trees")), experiment_path)

    mae_path = visualizer.save_validation_mae_comparison()
    rmse_path = visualizer.save_validation_rmse_comparison()
    r2_path = visualizer.save_validation_r2_comparison()

    assert mae_path == tmp_path / "reports" / "comparison" / "validation_mae_comparison.png"
    assert rmse_path == tmp_path / "reports" / "comparison" / "validation_rmse_comparison.png"
    assert r2_path == tmp_path / "reports" / "comparison" / "validation_r2_comparison.png"
    assert all(path.exists() for path in (mae_path, rmse_path, r2_path))


def test_experiment_visualizer_skips_empty_history(tmp_path: Path, mocker) -> None:
    mocker.patch(
        "ml_prediction.presentation.visual.experiment_visualizer.get_settings",
        return_value=mocker.Mock(
            audit_dir=tmp_path / "reports",
            experiment_filename="experiments.csv",
            comparison_dirname="comparison",
            validation_mae_filename="validation_mae_comparison.png",
            validation_rmse_filename="validation_rmse_comparison.png",
            validation_r2_filename="validation_r2_comparison.png",
        ),
    )
    visualizer = ExperimentVisualizer("house")
    visualizer._experiment_path = tmp_path / "experiments.csv"

    assert visualizer.save_validation_mae_comparison() is None
    assert visualizer.save_validation_rmse_comparison() is None
    assert visualizer.save_validation_r2_comparison() is None


