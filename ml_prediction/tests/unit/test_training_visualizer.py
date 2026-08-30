from pathlib import Path
from types import SimpleNamespace

import matplotlib

from ml_prediction.visualization.training_visualizer import TrainingVisualizer

import matplotlib.pyplot as plt


def test_save_figure_uses_headless_backend_and_closes_figure(tmp_path: Path) -> None:
    figure = plt.figure()
    output_path = tmp_path / "plots" / "training.png"

    saved_path = TrainingVisualizer.save_figure(figure, output_path)

    assert matplotlib.get_backend().lower() == "agg"
    assert saved_path == output_path
    assert output_path.exists()
    assert not plt.fignum_exists(figure.number)


def test_save_actual_vs_predicted_creates_experiment_artifact(tmp_path: Path) -> None:
    output_path = TrainingVisualizer.save_actual_vs_predicted(
        [1, 2, 3],
        [1.1, 1.9, 3.2],
        "experiment-1",
        tmp_path,
    )

    assert output_path == tmp_path / "experiment-1" / "actual_vs_predicted.png"
    assert output_path.exists()
    assert plt.get_fignums() == []


def test_save_residual_vs_predicted_creates_experiment_artifact(tmp_path: Path) -> None:
    output_path = TrainingVisualizer.save_residual_vs_predicted(
        [1, 2, 3],
        [1.1, 1.9, 3.2],
        "experiment-1",
        tmp_path,
    )

    assert output_path == tmp_path / "experiment-1" / "residual_vs_predicted.png"
    assert output_path.exists()
    assert plt.get_fignums() == []


def test_save_feature_importance_creates_experiment_artifact(tmp_path: Path) -> None:
    fitted_model = SimpleNamespace(
        pipeline=SimpleNamespace(
            named_steps={
                "preprocessor": SimpleNamespace(
                    get_feature_names_out=lambda: [
                        "numeric__area_sqm",
                        "categorical__city_Berlin",
                    ]
                ),
                "regressor": SimpleNamespace(feature_importances_=[0.2, 0.8]),
            }
        )
    )

    output_path = TrainingVisualizer.save_feature_importance(
        fitted_model,
        "experiment-1",
        tmp_path,
    )

    assert output_path == tmp_path / "experiment-1" / "feature_importance.png"
    assert output_path.exists()
    assert plt.get_fignums() == []


def test_save_feature_importance_skips_models_without_importances(tmp_path: Path) -> None:
    output_path = TrainingVisualizer.save_feature_importance(
        SimpleNamespace(),
        "experiment-1",
        tmp_path,
    )

    assert output_path is None
    assert not (tmp_path / "experiment-1" / "feature_importance.png").exists()


def test_feature_names_are_post_preprocessing_names_in_transform_order() -> None:
    pipeline = SimpleNamespace(
        named_steps={
            "preprocessor": SimpleNamespace(
                get_feature_names_out=lambda: [
                    "numeric__area_sqm",
                    "categorical__city_Berlin",
                    "categorical__city_Hamburg",
                ]
            )
        }
    )

    assert TrainingVisualizer._feature_names(pipeline, 3) == [
        "numeric__area_sqm",
        "categorical__city_Berlin",
        "categorical__city_Hamburg",
    ]
    assert TrainingVisualizer._feature_names(pipeline, 2) is None


def test_feature_importance_chart_limits_features_and_orders_by_importance(tmp_path: Path, mocker) -> None:
    feature_names = [f"feature_{index}" for index in range(25)]
    fitted_model = SimpleNamespace(
        pipeline=SimpleNamespace(
            named_steps={
                "preprocessor": SimpleNamespace(
                    get_feature_names_out=lambda: feature_names
                ),
                "regressor": SimpleNamespace(
                    feature_importances_=list(range(25))
                ),
            }
        )
    )
    save_figure = mocker.patch.object(TrainingVisualizer, "save_figure", return_value=tmp_path / "plot.png")

    TrainingVisualizer.save_feature_importance(fitted_model, "experiment-1", tmp_path)

    figure = save_figure.call_args.args[0]
    assert [label.get_text() for label in figure.axes[0].get_yticklabels()] == [
        f"feature_{index}" for index in range(24, 4, -1)
    ]
    assert len(figure.axes[0].patches) == 20
