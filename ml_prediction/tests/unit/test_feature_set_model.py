import pandas as pd
import pytest

from ml_prediction.config.dataset_profiles import HOUSE
from ml_prediction.model.dataset_split_model import DatasetSplitModel, FeaturesAndTargetModel
from ml_prediction.model.feature_set_model import FeatureSetModel

from conftest import make_dataframe

FEATURES = FeatureSetModel(numeric=("area",), boolean=("garden",), categorical=("city",))


def test_extract_selects_feature_columns_and_converts_booleans() -> None:
    dataframe = pd.DataFrame({"area": [1, 2], "garden": [True, "False"], "city": ["A", "B"], "other": [0, 0]})

    features = FEATURES.extract(dataframe)

    assert list(features.columns) == ["area", "garden", "city"]
    assert features["garden"].tolist() == [1, 0]


@pytest.mark.parametrize("dataframe, message", [
    (pd.DataFrame(), "must not be empty"),
    (pd.DataFrame([[1, 1, True, "A"]], columns=["area", "area", "garden", "city"]), "duplicated columns"),
    (pd.DataFrame({"area": [1], "garden": [True]}), "missing feature columns"),
])
def test_extract_rejects_invalid_datasets(dataframe, message) -> None:
    with pytest.raises(ValueError, match=message):
        FEATURES.extract(dataframe)


def test_extract_rejects_duplicated_feature_columns() -> None:
    with pytest.raises(ValueError, match="Feature columns are duplicated"):
        FeatureSetModel(numeric=("area", "area")).extract(pd.DataFrame({"area": [1]}))


def test_features_and_target_drop_rows_without_target() -> None:
    dataframe = make_dataframe(HOUSE, rows=10)
    dataframe.loc[0, HOUSE.target_column] = None

    data = FeaturesAndTargetModel.from_dataframe(dataframe, HOUSE.target_column, HOUSE.features)

    assert len(data) == 9
    assert HOUSE.target_column not in data.features.columns
    assert data.target.name == HOUSE.target_column


def test_dataset_is_split_into_train_validation_and_test() -> None:
    data = FeaturesAndTargetModel(pd.DataFrame({"value": range(10)}), pd.Series(range(10)))

    split = DatasetSplitModel.from_features(data, validation_size=0.2, test_size=0.2, random_state=42)

    assert (len(split.train), len(split.validation), len(split.test)) == (6, 2, 2)
    assert split.train.features.index.equals(split.train.target.index)
    assert set(split.train.features.index).isdisjoint(split.test.features.index)
