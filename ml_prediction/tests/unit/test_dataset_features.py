from pathlib import Path

import pandas as pd
import pytest

from ml_prediction.dataset.dataset import Dataset
from ml_prediction.dataset.house_dataset import HouseDataset
from ml_prediction.features.feature_builder import FeatureBuilder
from ml_prediction.features.feature_model import FeatureModel
from ml_prediction.features.house_feature_model import HouseFeatureModel
from ml_prediction.features.house_features_builder import HouseFeatureBuilder
from ml_prediction.utils.csv_utils import load_csv


def house_dataframe() -> pd.DataFrame:
    feature_model = HouseFeatureModel()
    data = {}
    for column in feature_model.get_numeric_features():
        data[column] = [1, 2]
    for column in feature_model.get_boolean_features():
        data[column] = [True, "False"]
    for column in feature_model.get_categorical_features():
        data[column] = ["A", "B"]
    return pd.DataFrame(data)


def test_dataset_and_feature_builder_are_concrete() -> None:
    assert not hasattr(Dataset, "__abstractmethods__")
    assert FeatureModel.__abstractmethods__ == {
        "get_numeric_features",
        "get_boolean_features",
        "get_categorical_features",
    }
    assert not hasattr(FeatureBuilder, "__abstractmethods__")


def test_house_dataset_loads_csv_and_prepares_numeric_target(tmp_path: Path) -> None:
    path = tmp_path / "house.csv"
    path.write_text("total_price,city\n100,Paris\ninvalid,London\n", encoding="utf-8")

    dataset = HouseDataset(path, "house")

    assert load_csv(path).shape == (2, 2)
    frame = dataset.training_frame("total_price")
    assert frame["total_price"].tolist() == ["100", "invalid"]


def test_house_feature_model_combines_feature_groups() -> None:
    model = HouseFeatureModel()

    assert model.get_feature_columns() == (
        model.get_numeric_features()
        + model.get_boolean_features()
        + model.get_categorical_features()
    )


def test_house_feature_builder_converts_booleans() -> None:
    dataframe = house_dataframe()
    features = HouseFeatureBuilder(dataframe, HouseFeatureModel()).build()

    assert features["owner_occupied"].tolist() == [1, 0]
    assert list(features.columns) == list(HouseFeatureModel().get_feature_columns())


def test_house_feature_builder_rejects_missing_columns() -> None:
    dataframe = house_dataframe().drop(columns=["city"])

    with pytest.raises(Exception, match="missing feature columns"):
        HouseFeatureBuilder(dataframe, HouseFeatureModel()).build()


def test_house_feature_builder_rejects_empty_dataframe() -> None:
    with pytest.raises(Exception, match="must not be empty"):
        HouseFeatureBuilder(pd.DataFrame(), HouseFeatureModel()).build()


def test_house_feature_builder_rejects_duplicated_dataframe_columns() -> None:
    dataframe = pd.DataFrame([[1, 2]], columns=["latitude", "latitude"])

    with pytest.raises(Exception, match="latitude"):
        HouseFeatureBuilder(dataframe, HouseFeatureModel()).build()


def test_house_feature_builder_rejects_invalid_feature_definition() -> None:
    model = HouseFeatureModel()
    model.get_numeric_features = lambda: ("",)

    with pytest.raises(Exception, match="''"):
        HouseFeatureBuilder(house_dataframe(), model).build()


def test_house_feature_builder_rejects_duplicated_feature_definition() -> None:
    model = HouseFeatureModel()
    model.get_boolean_features = lambda: ("latitude",)

    with pytest.raises(Exception, match="latitude"):
        HouseFeatureBuilder(house_dataframe(), model).build()
