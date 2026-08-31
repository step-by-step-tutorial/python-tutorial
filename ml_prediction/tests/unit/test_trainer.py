from pathlib import Path
from unittest.mock import call

import pandas as pd

from ml_prediction.data_model.app_settings import AppSettings, DatasetSource
from ml_prediction.data_model.datalake_settings import DataLakeSettings
from ml_prediction.data_model.evaluation import Evaluation
from ml_prediction.data_model.experiment import Experiment
from ml_prediction.data_model.features_and_target import FeaturesAndTarget
from ml_prediction.data_model.regression_metrics import RegressionMetrics
from ml_prediction.data_model.dataset_subset import DatasetSubset
from ml_prediction.data_model.dataset_split import DatasetSplit
from ml_prediction.data_model.training import TrainingOutput
from ml_prediction.reporting.report_service import ReportService
from ml_prediction.training.dataset_splitter import DatasetSplitter
from ml_prediction.training.house_price_trainer import HousePriceTrainer


def test_dataset_splitter_splits_dataset_into_train_validation_and_test() -> None:
    splitter = DatasetSplitter("house")
    features = pd.DataFrame({"value": range(10)})
    target = pd.Series(range(10), name="target")

    partitions = splitter.split(features, target)

    assert isinstance(partitions, DatasetSplit)
    assert len(partitions.train.features) == 6
    assert len(partitions.validation.features) == 2
    assert len(partitions.test.features) == 2
    assert set(partitions.train.features.index) == set(partitions.train.target.index)
    assert set(partitions.validation.features.index) == set(partitions.validation.target.index)
    assert set(partitions.test.features.index) == set(partitions.test.target.index)


def test_house_price_trainer_prepares_features_and_target(mocker) -> None:
    path = Path("house.csv")
    dataframe = pd.DataFrame({"target": [100, 200], "value": [1, 2]})
    expected_features = dataframe.drop(columns=["target"])
    features = pd.DataFrame({"value": [1, 2]})
    target = dataframe["target"]
    feature_builder = mocker.Mock()
    feature_builder.build.return_value = features

    trainer = HousePriceTrainer.__new__(HousePriceTrainer)
    trainer._dataset = mocker.Mock(path=path)
    trainer._settings = mocker.Mock(target_column="target")
    trainer._feature_model = mocker.Mock()
    feature_builder_class = mocker.patch(
        "ml_prediction.training.house_price_trainer.FeatureBuilder",
        return_value=feature_builder,
    )

    prepared = trainer.build_features_and_target(dataframe)

    assert isinstance(prepared, FeaturesAndTarget)
    assert prepared.features.equals(features)
    assert prepared.target.equals(target)
    assert feature_builder_class.call_count == 1
    assert feature_builder_class.call_args.args[0].equals(expected_features)
    assert feature_builder_class.call_args.args[1] is trainer._feature_model


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
        dataset_name="custom_dataset",
        dataset_filename="house.csv",
    )
    dataset_splitter = mocker.patch(
        "ml_prediction.training.house_price_trainer.DatasetSplitter",
        return_value=mocker.Mock(),
    ).return_value
    experiment_repository = mocker.patch(
        "ml_prediction.training.house_price_trainer.ExperimentService",
        return_value=mocker.Mock(),
    ).return_value
    training_visualizer = mocker.patch(
        "ml_prediction.training.house_price_trainer.TrainingVisualizer",
        return_value=mocker.Mock(),
    ).return_value
    experiment_visualizer = mocker.patch(
        "ml_prediction.training.house_price_trainer.ExperimentVisualizer",
        return_value=mocker.Mock(),
    ).return_value
    mocker.patch("ml_prediction.training.house_price_trainer.get_settings", return_value=settings)
    mocker.patch("ml_prediction.pipeline.regressor_builder.get_settings", return_value=settings)
    dataset = mocker.Mock(path=tmp_path / "data" / "house.csv", dataset_name=settings.dataset_name)
    trainer = HousePriceTrainer(dataset)
    dataset_path = tmp_path / "data" / "house.csv"
    dataframe = pd.DataFrame({"target": [100]})
    partition = DatasetSubset(dataframe, dataframe["target"])
    partitions = DatasetSplit(partition, partition, partition)
    model = mocker.Mock()
    metrics = RegressionMetrics(1.0, 2.0, 0.5)

    trainer.download_dataset = mocker.Mock(return_value=(dataframe, dataset_path))
    trainer.build_features_and_target = mocker.Mock(return_value=FeaturesAndTarget(dataframe, dataframe["target"]))
    dataset_splitter.split.return_value = partitions
    trainer.train_model = mocker.Mock(return_value=model)
    trainer.evaluate_model = mocker.Mock(side_effect=[metrics, metrics])
    trainer.evaluate_model_with_predictions = mocker.Mock(
        return_value=Evaluation([100], [100], metrics)
    )
    trainer.save_model = mocker.Mock(return_value=tmp_path / "models" / "house.joblib")

    result = trainer.train()

    assert isinstance(result, TrainingOutput)
    assert isinstance(result, Experiment)
    assert result.experiment_id
    assert result.timestamp.tzinfo is not None
    assert result.dataset_name == settings.dataset_name
    assert result.model_type == settings.model_type
    assert result.model_parameters["n_estimators"] == settings.n_estimators
    assert result.validation_metrics == metrics
    assert result.test_metrics == metrics
    assert result.model_path == tmp_path / "models" / "house.joblib"
    experiment_repository.save.assert_called_once_with(result)
    experiment_visualizer.save_validation_mae_comparison.assert_called_once_with()
    experiment_visualizer.save_validation_rmse_comparison.assert_called_once_with()
    experiment_visualizer.save_validation_r2_comparison.assert_called_once_with()
    trainer.build_features_and_target.assert_called_once_with(dataframe)
    dataset_splitter.split.assert_called_once_with(dataframe, dataframe["target"])
    trainer.train_model.assert_called_once_with(partitions)
    assert trainer.evaluate_model.call_count == 1
    trainer.evaluate_model_with_predictions.assert_called_once_with(model, partitions.test)
    assert trainer.evaluate_model.call_args_list == [
        call(model, partitions.validation),
    ]
    trainer.save_model.assert_called_once()
    training_visualizer.save_actual_vs_predicted.assert_called_once_with(
        [100], [100], result.experiment_id, settings.report_dir
    )
    training_visualizer.save_residual_vs_predicted.assert_called_once_with(
        [100], [100], result.experiment_id, settings.report_dir
    )
    training_visualizer.save_feature_importance.assert_called_once_with(
        model, result.experiment_id, settings.report_dir
    )
    assert result.report_path is not None
    assert result.report_path.exists()
    assert "training_completed" in result.report_path.read_text(encoding="utf-8")


def test_house_price_trainer_uses_local_dataset_without_download(tmp_path: Path, mocker) -> None:
    settings = AppSettings(
            data_dir=tmp_path / "data",
            model_dir=tmp_path / "models",
            target_column="target",
            validation_size=0.2,
            test_size=0.2,
            random_state=42,
            data_lake=DataLakeSettings("http://localhost", "key", "secret", "bucket", ""),
            dataset_source=DatasetSource.LOCAL,
            dataset_filename="house.csv",
            dataset_name="house",
    )
    mocker.patch("ml_prediction.training.house_price_trainer.get_settings", return_value=settings)
    dataset = mocker.Mock(path=tmp_path / "data" / "house.csv", dataset_name=settings.dataset_name)
    dataframe = pd.DataFrame()
    dataset.download.return_value = (dataframe, dataset.path)
    trainer = HousePriceTrainer(dataset)

    downloaded_dataframe, downloaded_path = trainer.download_dataset()
    assert downloaded_dataframe is dataframe
    assert downloaded_path == dataset.path
    dataset.download.assert_called_once_with()


def test_house_price_trainer_downloads_dataset_when_configured(tmp_path: Path, mocker) -> None:
    settings = AppSettings(
            data_dir=tmp_path / "data",
            model_dir=tmp_path / "models",
            target_column="target",
            validation_size=0.2,
            test_size=0.2,
            random_state=42,
            data_lake=DataLakeSettings("http://localhost", "key", "secret", "bucket", ""),
            dataset_source=DatasetSource.DOWNLOAD,
            dataset_filename="house.csv",
            dataset_name="house",
    )
    mocker.patch("ml_prediction.training.house_price_trainer.get_settings", return_value=settings)
    dataset = mocker.Mock(path=tmp_path / "data" / "house.csv", dataset_name=settings.dataset_name)
    dataframe = pd.DataFrame()
    dataset.download.return_value = (dataframe, dataset.path)
    trainer = HousePriceTrainer(dataset)

    downloaded_dataframe, downloaded_path = trainer.download_dataset()
    assert downloaded_dataframe is dataframe
    assert downloaded_path == dataset.path
    dataset.download.assert_called_once_with()
