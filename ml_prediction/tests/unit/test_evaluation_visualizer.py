from pathlib import Path
from types import SimpleNamespace

import matplotlib

from ml_prediction.visualize.evaluation_visualizer import EvaluationVisualizer
from ml_prediction.visualize.model_interpretability_visualizer import ModelInterpretabilityVisualizer
from ml_prediction.utils.pipeline_utils import get_feature_names

import matplotlib.pyplot as plt


def test_visualizer_uses_headless_backend() -> None:
    assert matplotlib.get_backend().lower() == "agg"


def test_save_actual_vs_predicted_creates_experiment_artifact(tmp_path: Path, mocker) -> None:
    settings = mocker.Mock(
        actual_vs_predicted_filename="actual_vs_predicted.png",
        residual_vs_predicted_filename="residual_vs_predicted.png",
        feature_importance_filename="feature_importance.png",
    )
    settings.artifact_path.side_effect = lambda run_id, filename: tmp_path / run_id / filename
    mocker.patch("ml_prediction.visualize.evaluation_visualizer.get_settings", return_value=settings)
    visualizer = EvaluationVisualizer("house")
    output_path = visualizer.save_actual_vs_predicted(
        [1, 2, 3],
        [1.1, 1.9, 3.2],
        "experiment-1",
    )

    assert output_path == tmp_path / "experiment-1" / "actual_vs_predicted.png"
    assert output_path.exists()
    assert plt.get_fignums() == []


def test_save_residual_vs_predicted_creates_experiment_artifact(tmp_path: Path, mocker) -> None:
    settings = mocker.Mock(residual_vs_predicted_filename="residual_vs_predicted.png")
    settings.artifact_path.side_effect = lambda run_id, filename: tmp_path / run_id / filename
    mocker.patch("ml_prediction.visualize.evaluation_visualizer.get_settings", return_value=settings)
    visualizer = EvaluationVisualizer("house")
    output_path = visualizer.save_residual_vs_predicted(
        [1, 2, 3],
        [1.1, 1.9, 3.2],
        "experiment-1",
    )

    assert output_path == tmp_path / "experiment-1" / "residual_vs_predicted.png"
    assert output_path.exists()
    assert plt.get_fignums() == []


def test_save_feature_importance_creates_experiment_artifact(tmp_path: Path, mocker) -> None:
    settings = mocker.Mock(feature_importance_filename="feature_importance.png")
    settings.artifact_path.side_effect = lambda run_id, filename: tmp_path / run_id / filename
    mocker.patch("ml_prediction.visualize.model_interpretability_visualizer.get_settings", return_value=settings)
    visualizer = ModelInterpretabilityVisualizer("house")
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

    output_path = visualizer.save_feature_importance(
        fitted_model,
        "experiment-1",
    )

    assert output_path == tmp_path / "experiment-1" / "feature_importance.png"
    assert output_path.exists()
    assert plt.get_fignums() == []


def test_save_feature_importance_skips_models_without_importances(tmp_path: Path) -> None:
    visualizer = ModelInterpretabilityVisualizer("house")
    output_path = visualizer.save_feature_importance(
        SimpleNamespace(),
        "experiment-1",
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

    assert get_feature_names(pipeline, 3) == [
        "numeric__area_sqm",
        "categorical__city_Berlin",
        "categorical__city_Hamburg",
    ]
    assert get_feature_names(pipeline, 2) is None


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
    settings = mocker.Mock(feature_importance_filename="feature_importance.png")
    settings.artifact_path.side_effect = lambda run_id, filename: tmp_path / run_id / filename
    mocker.patch("ml_prediction.visualize.model_interpretability_visualizer.get_settings", return_value=settings)
    visualizer = ModelInterpretabilityVisualizer("house")
    save_bar_chart = mocker.patch(
        "ml_prediction.visualize.model_interpretability_visualizer.save_bar_chart",
        return_value=tmp_path / "plot.png",
    )

    visualizer.save_feature_importance(fitted_model, "experiment-1")

    assert list(save_bar_chart.call_args.kwargs["labels"]) == [
        f"feature_{index}" for index in range(24, 4, -1)
    ]
    assert list(save_bar_chart.call_args.kwargs["values"]) == list(range(24, 4, -1))
    assert save_bar_chart.call_args.kwargs["horizontal"] is True


