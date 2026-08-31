from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import pytest

from ml_prediction.data_model.app_settings import AppSettings, DatasetSource
from ml_prediction.data_model.data_lake_settings import DataLakeSettings
from ml_prediction.inference.house_price_predictor import HousePricePredictor
from ml_prediction.data_model.prediction_output import PredictionOutput
from ml_prediction.inference.prediction_service import PredictionService
from ml_prediction.features.house_feature_model import HouseFeatureModel
from ml_prediction.features.house_features_builder import HouseFeatureBuilder
from ml_prediction.data_model.model_metadata import ModelMetadata
from ml_prediction.data_model.regression_metrics import RegressionMetrics
from ml_prediction.repository.datalake_repository import DataLakeRepository
from ml_prediction.repository.local_model_repository import LocalModelRepository

from test_dataset_features import house_dataframe


def settings(tmp_path: Path) -> AppSettings:
    return AppSettings(
        data_dir=tmp_path / "data",
        model_dir=tmp_path / "models",
        target_column="total_price",
        validation_size=0.2,
        test_size=0.2,
        random_state=42,
        data_lake=DataLakeSettings("http://localhost:9000", "key", "secret", "house", "prefix"),
        dataset_source=DatasetSource.DOWNLOAD,
        report_dir=tmp_path / "reports",
        dataset_filename="house.csv",
        model_filename="model.joblib",
        prediction_column="predicted_total_price",
    )


def test_local_model_repository_saves_and_loads(tmp_path: Path) -> None:
    repository = LocalModelRepository()
    path = tmp_path / "models" / "model.joblib"

    assert repository.save({"value": 1}, path) == path
    assert repository.load(path) == {"value": 1}


def test_local_model_repository_saves_and_loads_typed_metadata(tmp_path: Path) -> None:
    repository = LocalModelRepository()
    path = tmp_path / "models" / "model.joblib"
    metadata = ModelMetadata(
        model_type="random_forest",
        model_parameters={"n_estimators": 200, "n_jobs": -1, "random_state": 42},
        target_column="total_price",
        numeric_features=("area_sqm",),
        boolean_features=("has_garden",),
        categorical_features=("city",),
        training_timestamp=datetime.now(timezone.utc),
        validation_metrics=RegressionMetrics(1.0, 2.0, 0.5),
        final_test_metrics=RegressionMetrics(1.5, 2.5, 0.4),
        schema_version="1",
        model_version="1",
    )

    repository.save({"value": 1}, path, metadata)

    assert repository.load_metadata(path) == metadata


def test_datalake_repository_lists_only_parquet_objects(mocker) -> None:
    client = mocker.Mock()
    client.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "prefix/old.parquet", "LastModified": 1},
            {"Key": "prefix/new.PARQUET", "LastModified": 2},
            {"Key": "prefix/ignored.json", "LastModified": 3},
        ]
    }
    mocker.patch("ml_prediction.repository.datalake_repository.boto3.client", return_value=client)
    repository = DataLakeRepository("house")

    assert [item["Key"] for item in repository.get_object_keys()] == ["prefix/old.parquet", "prefix/new.PARQUET"]
    client.list_objects_v2.assert_called_once_with(Bucket="house", Prefix="enriched/house/")


def test_datalake_repository_downloads_latest_partition_as_csv(tmp_path: Path, mocker) -> None:
    client = mocker.Mock()
    client.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "enriched/house/old/part-1.parquet", "LastModified": 1},
            {"Key": "enriched/house/new/part-1.parquet", "LastModified": 2},
            {"Key": "enriched/house/new/part-2.parquet", "LastModified": 3},
        ]
    }
    mocker.patch("ml_prediction.repository.datalake_repository.boto3.client", return_value=client)
    mocker.patch("ml_prediction.repository.datalake_repository.pd.read_parquet", side_effect=[
        pd.DataFrame({"value": [1]}),
        pd.DataFrame({"value": [2]}),
    ])
    repository = DataLakeRepository("house")
    output = tmp_path / "data" / "house.csv"

    assert repository.download_latest_csv(output) == output
    assert output.read_text(encoding="utf-8") == "value\n1\n2\n"
    assert [call.args[1] for call in client.download_fileobj.call_args_list] == [
        "enriched/house/new/part-1.parquet",
        "enriched/house/new/part-2.parquet",
    ]


def test_datalake_repository_rejects_empty_bucket(tmp_path: Path, mocker) -> None:
    client = mocker.Mock()
    client.list_objects_v2.return_value = {}
    mocker.patch("ml_prediction.repository.datalake_repository.boto3.client", return_value=client)

    with pytest.raises(FileNotFoundError, match="No Parquet files found"):
        DataLakeRepository("house").download_latest_csv(tmp_path / "house.csv")


def test_prediction_service_downloads_loads_and_predicts(mocker, tmp_path: Path) -> None:
    dataset_path = tmp_path / "data" / "house.csv"
    dataset = mocker.Mock(path=dataset_path, dataset_name="house")
    dataframe = pd.DataFrame({"total_price": [100]})
    dataset_path.parent.mkdir(parents=True)
    dataframe.to_csv(dataset_path, index=False)
    predictor = mocker.Mock()
    predictor.predict.return_value = pd.Series([110])
    mocker.patch(
        "ml_prediction.inference.prediction_service.get_settings",
        return_value=settings(tmp_path),
    )
    mocker.patch("ml_prediction.inference.prediction_service.DataLakeRepository")
    service = PredictionService(predictor, dataset)
    mocker.patch.object(service, "download_dataset", return_value=dataset_path)

    result = service.predict()

    assert isinstance(result, PredictionOutput)
    pd.testing.assert_frame_equal(result.dataframe, dataframe)
    assert result.predictions.tolist() == [110]
    assert result.report_path is not None
    assert result.report_path.exists()
    assert "prediction_completed" in result.report_path.read_text(encoding="utf-8")
    predictor.predict.assert_called_once()
    pd.testing.assert_frame_equal(predictor.predict.call_args.args[0], dataframe)


def test_prediction_service_uses_local_dataset_without_download(mocker, tmp_path: Path) -> None:
    repository = mocker.Mock()
    local_settings = AppSettings(
        data_dir=tmp_path / "data",
        model_dir=tmp_path / "models",
        target_column="total_price",
        validation_size=0.2,
        test_size=0.2,
        random_state=42,
        data_lake=DataLakeSettings("http://localhost", "key", "secret", "house", ""),
        dataset_source=DatasetSource.LOCAL,
        dataset_filename="house.csv",
    )
    mocker.patch(
        "ml_prediction.inference.prediction_service.get_settings",
        return_value=local_settings,
    )
    mocker.patch(
        "ml_prediction.inference.prediction_service.DataLakeRepository",
        return_value=repository,
    )
    service = PredictionService(
        mocker.Mock(dataset_name="house"),
        mocker.Mock(),
    )

    assert service.download_dataset() == tmp_path / "data" / "house.csv"
    repository.return_value.download_latest_csv.assert_not_called()


def test_prediction_service_downloads_dataset_when_configured(mocker, tmp_path: Path) -> None:
    repository = mocker.Mock()
    mocker.patch(
        "ml_prediction.inference.prediction_service.get_settings",
        return_value=settings(tmp_path),
    )
    mocker.patch(
        "ml_prediction.inference.prediction_service.DataLakeRepository",
        return_value=repository,
    )
    service = PredictionService(mocker.Mock(), mocker.Mock(dataset_name="house"))

    assert service.download_dataset() == tmp_path / "data" / "house.csv"
    repository.download_latest_csv.assert_called_once_with(
        tmp_path / "data" / "house.csv"
    )


def test_prediction_service_rejects_dataset_path_mismatch(mocker, tmp_path: Path) -> None:
    dataset = mocker.Mock(path=tmp_path / "different.csv", dataset_name="house")
    mocker.patch(
        "ml_prediction.inference.prediction_service.get_settings",
        return_value=settings(tmp_path),
    )
    mocker.patch("ml_prediction.inference.prediction_service.DataLakeRepository")
    service = PredictionService(
        mocker.Mock(),
        dataset,
    )
    downloaded_path = tmp_path / "data" / "house.csv"
    mocker.patch.object(service, "download_dataset", return_value=downloaded_path)

    with pytest.raises(ValueError, match="does not match downloaded path"):
        service.predict()


def test_house_price_predictor_builds_features_and_returns_named_series(mocker) -> None:
    pipeline = mocker.Mock()
    pipeline.predict.return_value = [101.0, 202.0]
    repository = mocker.Mock()
    repository.load.return_value = pipeline
    repository.load_metadata.return_value = ModelMetadata(
        model_type="random_forest",
        model_parameters={"n_estimators": 200, "n_jobs": -1, "random_state": 42},
        target_column="total_price",
        numeric_features=HouseFeatureModel().get_numeric_features(),
        boolean_features=HouseFeatureModel().get_boolean_features(),
        categorical_features=HouseFeatureModel().get_categorical_features(),
        training_timestamp=datetime.now(timezone.utc),
        validation_metrics=RegressionMetrics(1.0, 2.0, 0.5),
        final_test_metrics=RegressionMetrics(1.5, 2.5, 0.4),
        schema_version="1",
        model_version="1",
    )
    mocker.patch(
        "ml_prediction.inference.model_predictor.get_settings",
        return_value=settings(Path(".")),
    )
    mocker.patch(
        "ml_prediction.inference.model_predictor.LocalModelRepository",
        return_value=repository,
    )
    predictor = HousePricePredictor(
        "house",
        HouseFeatureModel(),
    )

    predictions = predictor.predict(house_dataframe())

    assert predictions.tolist() == [101.0, 202.0]
    assert predictions.name == "predicted_total_price"
    repository.load.assert_called_once_with(Path("models") / "model.joblib")
    pipeline.predict.assert_called_once()

