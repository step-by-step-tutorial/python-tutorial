import pytest

from conftest import make_dataframe
from ml_prediction.config.dataset_profiles import HOUSE, ONLINE_SHOPPING
from ml_prediction.config.model_type import ModelType
from ml_prediction.estimator import model_selector
from ml_prediction.estimator.model_selector import ModelSelector
from ml_prediction.estimator.pipeline_factory import create_estimator, create_pipeline
from ml_prediction.model.dataset_profile_model import DatasetProfileModel
from ml_prediction.model.dataset_split_model import FeaturesAndTargetModel
from ml_prediction.model.settings_model import ModelParametersModel


@pytest.fixture(autouse=True)
def small_search_grid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(model_selector.SEARCH_GRIDS, ModelType.RANDOM_FOREST, {"max_depth": [2, 4]})


def select(profile: DatasetProfileModel):
    data = FeaturesAndTargetModel.from_dataframe(make_dataframe(profile), profile.target_column, profile.features)
    estimator = create_estimator(profile.task_type, ModelType.RANDOM_FOREST,
                                 ModelParametersModel(n_estimators=5, n_jobs=1))
    pipeline = create_pipeline(profile.features, estimator)
    return ModelSelector(n_jobs=1).select(pipeline, data, profile.task_type, ModelType.RANDOM_FOREST)


def test_regression_search_reports_positive_mean_absolute_error() -> None:
    selection = select(HOUSE)

    assert selection.metric == "mean_absolute_error"
    assert selection.score > 0
    assert set(selection.parameters) == {"max_depth"}
    assert selection.parameters["max_depth"] in {2, 4}


def test_classification_search_reports_weighted_f1() -> None:
    selection = select(ONLINE_SHOPPING)

    assert selection.metric == "f1_weighted"
    assert 0 <= selection.score <= 1
