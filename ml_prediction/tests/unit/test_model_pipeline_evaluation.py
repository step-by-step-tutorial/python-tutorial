import pandas as pd
import pytest
from sklearn.ensemble import (
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.pipeline import Pipeline

from ml_prediction.data_model.evaluation_result import Evaluation
from ml_prediction.evaluation.model_evaluator import ModelEvaluator
from ml_prediction.data_model.regression_metrics import RegressionMetrics
from ml_prediction.features.house_feature_model import HouseFeatureModel
from ml_prediction.features.house_features_builder import HouseFeatureBuilder
from ml_prediction.model.house_price_model import HousePriceModel
from ml_prediction.model.model import Model
from ml_prediction.pipeline.house_price_pipeline_builder import HousePricePipelineBuilder
from ml_prediction.pipeline.pipeline_builder import PipelineBuilder
from ml_prediction.pipeline.regressor_builder import RegressorBuilder

from test_dataset_features import house_dataframe


def test_pipeline_builder_is_abstract_and_builds_pipeline() -> None:
    feature_model = HouseFeatureModel()
    builder = HousePricePipelineBuilder(feature_model, RegressorBuilder("random_forest", 200, -1, 42))

    assert issubclass(HousePricePipelineBuilder, PipelineBuilder)
    pipeline = builder.build()
    assert list(pipeline.named_steps) == ["preprocessor", "regressor"]
    assert pipeline.named_steps["preprocessor"].transformers[0][0] == "numeric"
    assert pipeline.named_steps["preprocessor"].transformers[1][0] == "categorical"
    assert pipeline.named_steps["regressor"].n_estimators == 200


def test_regressor_builder_builds_configured_random_forest() -> None:
    regressor = RegressorBuilder(
        "random_forest",
        17,
        3,
        42,
        max_depth=8,
        min_samples_split=4,
        min_samples_leaf=2,
        max_features=0.7,
        bootstrap=False,
    ).build()

    assert regressor.n_estimators == 17
    assert regressor.n_jobs == 3
    assert regressor.random_state == 42
    assert regressor.max_depth == 8
    assert regressor.min_samples_split == 4
    assert regressor.min_samples_leaf == 2
    assert regressor.max_features == 0.7
    assert regressor.bootstrap is False


@pytest.mark.parametrize(
    ("model_type", "expected_type"),
    [
        ("random_forest", RandomForestRegressor),
        ("extra_trees", ExtraTreesRegressor),
        ("gradient_boosting", GradientBoostingRegressor),
        ("hist_gradient_boosting", HistGradientBoostingRegressor),
    ],
)
def test_regressor_builder_supports_configured_model_types(model_type, expected_type) -> None:
    regressor = RegressorBuilder(
        model_type,
        17,
        3,
        42,
        max_depth=8,
        min_samples_split=4,
        min_samples_leaf=2,
        max_features=0.7,
        bootstrap=False,
    ).build()

    assert isinstance(regressor, expected_type)
    assert regressor.random_state == 42


def test_regressor_builder_rejects_unsupported_model_type() -> None:
    with pytest.raises(ValueError, match="Unsupported model type: linear"):
        RegressorBuilder("linear", 200, -1, 42).build()


def test_house_price_model_fits_and_predicts() -> None:
    dataframe = house_dataframe()
    features = HouseFeatureBuilder(dataframe, HouseFeatureModel()).build()
    target = pd.Series([100, 200])
    model = HousePriceModel(
        HousePricePipelineBuilder(
            HouseFeatureModel(),
            RegressorBuilder("random_forest", 200, -1, 42),
        )
    )

    assert isinstance(model, Model)
    assert model.fit(features, target) is model
    assert isinstance(model.pipeline, Pipeline)
    assert list(model.pipeline.named_steps) == ["preprocessor", "regressor"]
    assert len(model.predict(features)) == 2


def test_model_evaluator_returns_regression_metrics() -> None:
    metrics = ModelEvaluator().evaluate([100, 200], [110, 180]).metrics

    assert isinstance(metrics, RegressionMetrics)
    assert metrics.mean_absolute_error == 15.0
    assert metrics.root_mean_squared_error == 15.811388300841896
    assert metrics.r2_score == 0.9


def test_model_evaluator_exposes_predictions_and_metrics() -> None:
    actual = [100, 200]
    predicted = [110, 180]

    result = ModelEvaluator().evaluate(actual, predicted)

    assert isinstance(result, Evaluation)
    assert result.y_true == actual
    assert result.y_pred == predicted
    assert result.metrics == RegressionMetrics(15.0, 15.811388300841896, 0.9)
