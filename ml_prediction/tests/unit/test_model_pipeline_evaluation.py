import pandas as pd

from ml_prediction.evaluation.model_evaluator import ModelEvaluator, RegressionMetrics
from ml_prediction.features.house_feature_model import HouseFeatureModel
from ml_prediction.features.house_features import HouseFeatureBuilder
from ml_prediction.model.house_price_model import HousePriceModel
from ml_prediction.model.model import Model
from ml_prediction.pipeline.house_price_pipeline_builder import HousePricePipelineBuilder
from ml_prediction.pipeline.pipeline_builder import PipelineBuilder

from test_dataset_features import house_dataframe


def test_pipeline_builder_is_abstract_and_builds_pipeline() -> None:
    feature_model = HouseFeatureModel()
    builder = HousePricePipelineBuilder(feature_model, 42)

    assert issubclass(HousePricePipelineBuilder, PipelineBuilder)
    pipeline = builder.build()
    assert list(pipeline.named_steps) == ["preprocessor", "regressor"]


def test_house_price_model_fits_and_predicts() -> None:
    dataframe = house_dataframe()
    features = HouseFeatureBuilder(dataframe, HouseFeatureModel()).build()
    target = pd.Series([100, 200])
    model = HousePriceModel(HousePricePipelineBuilder(HouseFeatureModel(), 42))

    assert isinstance(model, Model)
    assert model.fit(features, target) is model
    assert len(model.predict(features)) == 2


def test_model_evaluator_returns_regression_metrics() -> None:
    metrics = ModelEvaluator([100, 200], [110, 180]).evaluate()

    assert isinstance(metrics, RegressionMetrics)
    assert metrics.mean_absolute_error == 15.0
    assert metrics.root_mean_squared_error == 15.811388300841896
    assert metrics.r2_score == 0.9
