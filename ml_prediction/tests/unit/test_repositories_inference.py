from pathlib import Path

import pandas as pd
import pytest

from ml_prediction.config.settings import AppSettings, DataLakeSettings, DatasetSource
from ml_prediction.inference.house_price_predictor import HousePricePredictor
from ml_prediction.inference.prediction_service import PredictionOutput, PredictionService
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
    )


def test_local_model_repository_saves_and_loads(tmp_path: Path) -> None:
    repository = LocalModelRepository()
    path = tmp_path / "models" / "model.joblib"

    assert repository.save({"value": 1}, path) == path
    assert repository.load(path) == {"value": 1}


def test_datalake_repository_lists_only_csv_objects(mocker) -> None:
    client = mocker.Mock()
    client.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "prefix/old.csv", "LastModified": 1},
            {"Key": "prefix/new.CSV", "LastModified": 2},
            {"Key": "prefix/ignored.json", "LastModified": 3},
        ]
    }
    mocker.patch("ml_prediction.repository.datalake_repository.boto3.client", return_value=client)
    repository = DataLakeRepository(settings(Path("/tmp" )).data_lake)

    assert [item["Key"] for item in repository.get_object_keys()] == ["prefix/old.csv", "prefix/new.CSV"]
    client.list_objects_v2.assert_called_once_with(Bucket="house", Prefix="prefix")


def test_datalake_repository_downloads_latest_csv(tmp_path: Path, mocker) -> None:
    client = mocker.Mock()
    client.list_objects_v2.return_value = {
        "Contents": [
            {"Key": "old.csv", "LastModified": 1, "Size": 1},
            {"Key": "new.csv", "LastModified": 2, "Size": 2},
        ]
    }
    mocker.patch("ml_prediction.repository.datalake_repository.boto3.client", return_value=client)
    repository = DataLakeRepository(settings(tmp_path).data_lake)
    output = tmp_path / "data" / "house.csv"

    assert repository.download_latest_csv(output) == output
    client.download_file.assert_called_once_with("house", "new.csv", str(output))


def test_datalake_repository_rejects_empty_bucket(tmp_path: Path, mocker) -> None:
    client = mocker.Mock()
    client.list_objects_v2.return_value = {}
    mocker.patch("ml_prediction.repository.datalake_repository.boto3.client", return_value=client)

    with pytest.raises(FileNotFoundError, match="No CSV files found"):
        DataLakeRepository(settings(tmp_path).data_lake).download_latest_csv(tmp_path / "house.csv")


def test_prediction_service_downloads_loads_and_predicts(mocker, tmp_path: Path) -> None:
    dataset_path = tmp_path / "data" / "house.csv"
    dataset = mocker.Mock(path=dataset_path)
    dataframe = pd.DataFrame({"total_price": [100]})
    dataset.load.return_value = dataframe
    predictor = mocker.Mock()
    predictor.predict.return_value = pd.Series([110])
    service = PredictionService(settings(tmp_path), predictor, dataset)
    mocker.patch.object(service, "download_dataset", return_value=dataset_path)

    result = service.predict()

    assert isinstance(result, PredictionOutput)
    assert result.dataframe is dataframe
    assert result.predictions.tolist() == [110]
    assert result.report_path is not None
    assert result.report_path.exists()
    assert "prediction_completed" in result.report_path.read_text(encoding="utf-8")
    predictor.predict.assert_called_once_with(dataframe)


def test_prediction_service_uses_local_dataset_without_download(mocker, tmp_path: Path) -> None:
    repository = mocker.patch("ml_prediction.inference.prediction_service.DataLakeRepository")
    service = PredictionService(
        AppSettings(
            data_dir=tmp_path / "data",
            model_dir=tmp_path / "models",
            target_column="total_price",
            validation_size=0.2,
            test_size=0.2,
            random_state=42,
            data_lake=DataLakeSettings("http://localhost", "key", "secret", "house", ""),
            dataset_source=DatasetSource.LOCAL,
        ),
        mocker.Mock(),
        mocker.Mock(),
    )

    assert service.download_dataset() == tmp_path / "data" / "house.csv"
    repository.return_value.download_latest_csv.assert_not_called()


def test_prediction_service_downloads_dataset_when_configured(mocker, tmp_path: Path) -> None:
    repository = mocker.patch("ml_prediction.inference.prediction_service.DataLakeRepository")
    service = PredictionService(settings(tmp_path), mocker.Mock(), mocker.Mock())

    assert service.download_dataset() == tmp_path / "data" / "house.csv"
    repository.return_value.download_latest_csv.assert_called_once_with(
        tmp_path / "data" / "house.csv"
    )


def test_prediction_service_rejects_dataset_path_mismatch(mocker, tmp_path: Path) -> None:
    dataset = mocker.Mock(path=tmp_path / "different.csv")
    service = PredictionService(
        settings(tmp_path),
        mocker.Mock(),
        dataset,
    )
    downloaded_path = tmp_path / "data" / "house.csv"
    mocker.patch.object(service, "download_dataset", return_value=downloaded_path)

    with pytest.raises(ValueError, match="does not match downloaded path"):
        service.predict()


def test_house_price_predictor_builds_features_and_returns_named_series(mocker) -> None:
    model = mocker.Mock()
    model.predict.return_value = [101.0, 202.0]
    repository = mocker.Mock()
    repository.load.return_value = model
    predictor = HousePricePredictor(Path("model.joblib"), repository)

    predictions = predictor.predict(house_dataframe())

    assert predictions.tolist() == [101.0, 202.0]
    assert predictions.name == "predicted_total_price"
    model.predict.assert_called_once()
