from pathlib import Path

import pandas as pd

from ml_prediction.config.settings import AppSettings, DataLakeSettings, DatasetSource
from ml_prediction.dataset.house_dataset import PreparedTrainingData
from ml_prediction.evaluation.model_evaluator import RegressionMetrics
from ml_prediction.training.dataset_splitter import DatasetSplitter
from ml_prediction.training.house_price_trainer import HousePriceTrainer
from ml_prediction.training.training_models import DatasetPartition, DatasetPartitions, TrainingOutput


def test_dataset_splitter_splits_dataset_into_train_validation_and_test() -> None:
    splitter = DatasetSplitter(0.2, 0.2, 42)
    features = pd.DataFrame({"value": range(10)})
    target = pd.Series(range(10), name="target")

    partitions = splitter.split(features, target)

    assert isinstance(partitions, DatasetPartitions)
    assert len(partitions.train.features) == 6
    assert len(partitions.validation.features) == 2
    assert len(partitions.test.features) == 2
    assert set(partitions.train.features.index) == set(partitions.train.target.index)
    assert set(partitions.validation.features.index) == set(partitions.validation.target.index)
    assert set(partitions.test.features.index) == set(partitions.test.target.index)


def test_house_price_trainer_training_workflow_coordinates_all_steps(tmp_path: Path, mocker) -> None:
    settings = AppSettings(
        data_dir=tmp_path / "data",
        model_dir=tmp_path / "models",
        target_column="target",
        validation_size=0.2,
        test_size=0.2,
        random_state=42,
        data_lake=DataLakeSettings("http://localhost", "key", "secret", "bucket", ""),
        report_dir=tmp_path / "reports",
    )
    dataset_splitter = mocker.Mock()
    trainer = HousePriceTrainer(
        settings,
        mocker.Mock(),
        mocker.Mock(),
        mocker.Mock(),
        mocker.Mock(),
        mocker.Mock(),
        mocker.Mock(),
        dataset_splitter,
    )
    dataset_path = tmp_path / "data" / "house.csv"
    dataframe = pd.DataFrame({"target": [100]})
    partition = DatasetPartition(dataframe, dataframe["target"])
    partitions = DatasetPartitions(partition, partition, partition)
    baseline = mocker.Mock()
    model = mocker.Mock()
    metrics = RegressionMetrics(1.0, 2.0, 0.5)

    trainer.download_dataset = mocker.Mock(return_value=dataset_path)
    trainer.prepare_dataset = mocker.Mock(return_value=PreparedTrainingData(dataframe, dataframe["target"]))
    dataset_splitter.split.return_value = partitions
    trainer.train_baseline = mocker.Mock(return_value=baseline)
    trainer.train_model = mocker.Mock(return_value=model)
    trainer.evaluate_model = mocker.Mock(side_effect=[metrics, metrics, metrics])
    trainer.save_model = mocker.Mock(return_value=tmp_path / "models" / "house.joblib")

    result = trainer.train()

    assert isinstance(result, TrainingOutput)
    trainer.prepare_dataset.assert_called_once_with(dataset_path)
    dataset_splitter.split.assert_called_once_with(dataframe, dataframe["target"])
    trainer.train_baseline.assert_called_once_with(partitions)
    trainer.train_model.assert_called_once_with(partitions)
    assert trainer.evaluate_model.call_count == 3
    trainer.save_model.assert_called_once_with(model)
    assert result.report_path is not None
    assert result.report_path.exists()
    assert "training_completed" in result.report_path.read_text(encoding="utf-8")


def test_house_price_trainer_uses_local_dataset_without_download(tmp_path: Path, mocker) -> None:
    storage_repository = mocker.Mock()
    trainer = HousePriceTrainer(
        AppSettings(
            data_dir=tmp_path / "data",
            model_dir=tmp_path / "models",
            target_column="target",
            validation_size=0.2,
            test_size=0.2,
            random_state=42,
            data_lake=DataLakeSettings("http://localhost", "key", "secret", "bucket", ""),
            dataset_source=DatasetSource.LOCAL,
        ),
        mocker.Mock(),
        mocker.Mock(),
        storage_repository,
        mocker.Mock(),
        mocker.Mock(),
        mocker.Mock(),
        mocker.Mock(),
    )

    assert trainer.download_dataset() == tmp_path / "data" / "house.csv"
    storage_repository.download_latest_csv.assert_not_called()


def test_house_price_trainer_downloads_dataset_when_configured(tmp_path: Path, mocker) -> None:
    storage_repository = mocker.Mock()
    trainer = HousePriceTrainer(
        AppSettings(
            data_dir=tmp_path / "data",
            model_dir=tmp_path / "models",
            target_column="target",
            validation_size=0.2,
            test_size=0.2,
            random_state=42,
            data_lake=DataLakeSettings("http://localhost", "key", "secret", "bucket", ""),
            dataset_source=DatasetSource.DOWNLOAD,
        ),
        mocker.Mock(),
        mocker.Mock(),
        storage_repository,
        mocker.Mock(),
        mocker.Mock(),
        mocker.Mock(),
        mocker.Mock(),
    )

    assert trainer.download_dataset() == tmp_path / "data" / "house.csv"
    storage_repository.download_latest_csv.assert_called_once_with(
        tmp_path / "data" / "house.csv"
    )
