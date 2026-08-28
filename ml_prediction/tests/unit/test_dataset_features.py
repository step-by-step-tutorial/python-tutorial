from pathlib import Path

import pandas as pd
import pytest

from ml_prediction.dataset.dataset import Dataset
from ml_prediction.dataset.house_dataset import HouseDataset, PreparedTrainingData
from ml_prediction.features.feature_builder import FeatureBuilder
from ml_prediction.features.feature_model import FeatureModel
from ml_prediction.features.house_feature_model import HouseFeatureModel
from ml_prediction.features.house_features import HouseFeatureBuilder


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


def test_dataset_and_feature_builder_are_abstract() -> None:
    assert Dataset.__abstractmethods__ == {"load"}
    assert FeatureModel.__abstractmethods__ == {
        "get_numeric_features",
        "get_boolean_features",
        "get_categorical_features",
    }
    assert FeatureBuilder.__abstractmethods__ == {"build"}


def test_house_dataset_loads_csv_and_prepares_numeric_target(tmp_path: Path) -> None:
    path = tmp_path / "house.csv"
    path.write_text("total_price,city\n100,Paris\ninvalid,London\n", encoding="utf-8")

    dataset = HouseDataset(path)

    assert dataset.load().shape == (2, 2)
    frame = dataset.training_frame("total_price")
    assert frame["total_price"].tolist() == [100]


def test_house_dataset_prepares_features_and_target(tmp_path: Path) -> None:
    dataframe = house_dataframe()
    dataframe["total_price"] = [100, 200]
    path = tmp_path / "house.csv"
    dataframe.to_csv(path, index=False)

    prepared = HouseDataset(path).prepare_training_data(
        "total_price",
        lambda frame: HouseFeatureBuilder(frame, HouseFeatureModel()),
    )

    assert isinstance(prepared, PreparedTrainingData)
    assert prepared.target.tolist() == [100, 200]
    assert "total_price" not in prepared.features.columns


def test_house_dataset_rejects_missing_target_column(tmp_path: Path) -> None:
    path = tmp_path / "house.csv"
    path.write_text("city\nParis\n", encoding="utf-8")

    with pytest.raises(ValueError, match="total_price"):
        HouseDataset(path).training_frame("total_price")


def test_house_dataset_rejects_empty_dataset(tmp_path: Path) -> None:
    path = tmp_path / "house.csv"
    path.write_text("total_price,city\n", encoding="utf-8")

    with pytest.raises(ValueError, match="must not be empty"):
        HouseDataset(path).training_frame("total_price")


def test_house_dataset_rejects_target_without_usable_numeric_values(tmp_path: Path) -> None:
    path = tmp_path / "house.csv"
    path.write_text("total_price,city\ninvalid,Paris\nunknown,London\n", encoding="utf-8")

    with pytest.raises(ValueError, match="total_price"):
        HouseDataset(path).training_frame("total_price")


def test_house_dataset_rejects_duplicated_column_names(tmp_path: Path) -> None:
    path = tmp_path / "house.csv"
    path.write_text("total_price,city,city\n100,Paris,Paris\n", encoding="utf-8")

    with pytest.raises(ValueError, match="city"):
        HouseDataset(path).training_frame("total_price")


def test_house_dataset_preparation_delegates_missing_features_to_builder(tmp_path: Path) -> None:
    dataframe = house_dataframe()
    dataframe["total_price"] = [100, 200]
    dataframe = dataframe.drop(columns=["city"])
    path = tmp_path / "house.csv"
    dataframe.to_csv(path, index=False)

    with pytest.raises(ValueError, match="city"):
        HouseDataset(path).prepare_training_data(
            "total_price",
            lambda frame: HouseFeatureBuilder(frame, HouseFeatureModel()),
        )


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

    with pytest.raises(ValueError, match="missing feature columns"):
        HouseFeatureBuilder(dataframe, HouseFeatureModel()).build()


def test_house_feature_builder_rejects_empty_dataframe() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        HouseFeatureBuilder(pd.DataFrame(), HouseFeatureModel()).build()


def test_house_feature_builder_rejects_duplicated_dataframe_columns() -> None:
    dataframe = pd.DataFrame([[1, 2]], columns=["latitude", "latitude"])

    with pytest.raises(ValueError, match="latitude"):
        HouseFeatureBuilder(dataframe, HouseFeatureModel()).build()


def test_house_feature_builder_rejects_invalid_feature_definition() -> None:
    model = HouseFeatureModel()
    model.get_numeric_features = lambda: ("",)

    with pytest.raises(ValueError, match="''"):
        HouseFeatureBuilder(house_dataframe(), model).build()


def test_house_feature_builder_rejects_duplicated_feature_definition() -> None:
    model = HouseFeatureModel()
    model.get_boolean_features = lambda: ("latitude",)

    with pytest.raises(ValueError, match="latitude"):
        HouseFeatureBuilder(house_dataframe(), model).build()
