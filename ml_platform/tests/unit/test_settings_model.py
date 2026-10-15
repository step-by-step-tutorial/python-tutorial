from pathlib import Path

from ml_platform.config.dataset_source import DatasetSource
from ml_platform.config.dataset_profiles import HOUSE, ONLINE_SHOPPING
from ml_platform.config.model_type import ModelType
from ml_platform.config.operation import Operation
from ml_platform.model.settings_model import SettingsModel


def test_defaults_are_read_from_the_project_root() -> None:
    settings = SettingsModel.from_env(HOUSE, environ={"PROJECT_ROOT": "/project"})

    assert settings.dataset_path == Path("/project/data/house.csv")
    assert settings.model_path == Path("/project/models/house_model.joblib")
    assert settings.prediction_path == Path("/project/output/house_predictions.csv")
    assert settings.experiment_path == Path("/project/audit_log/house_experiments.csv")
    assert settings.execution_log_path(Operation.TRAIN, "run") == Path("/project/audit_log/house_train_run.csv")
    assert settings.artifact_path("run", "plot.png") == Path("/project/audit_log/run/plot.png")
    assert settings.comparison_path("mae.png") == Path("/project/audit_log/comparison/house_mae.png")
    assert settings.dataset_source == DatasetSource.LOCAL
    assert settings.model_type == ModelType.RANDOM_FOREST
    assert settings.model_parameters.bootstrap is True
    assert settings.model_parameters.max_depth is None
    assert settings.search_enabled is False
    assert settings.mlflow.enabled is False


def test_environment_overrides_defaults() -> None:
    settings = SettingsModel.from_env(HOUSE, environ={
        "ML_PLATFORM_MODEL_TYPE": "extra_trees",
        "ML_PLATFORM_BOOTSTRAP": "false",
        "ML_PLATFORM_MAX_DEPTH": "12",
        "ML_PLATFORM_RANDOM_STATE": "7",
        "ML_PLATFORM_DATASET_SOURCE": "download",
        "ML_PLATFORM_SEARCH_ENABLED": "true",
        "MLFLOW_ENABLED": "yes",
        "EXECUTION_LOG_ENABLED": "0",
    })

    assert settings.model_type == ModelType.EXTRA_TREES
    assert settings.model_parameters.bootstrap is False
    assert settings.model_parameters.max_depth == 12
    assert settings.model_parameters.random_state == 7
    assert settings.dataset_source == DatasetSource.DOWNLOAD
    assert settings.search_enabled is True
    assert settings.mlflow.enabled is True
    assert settings.execution_log_enabled is False


def test_search_flag_enables_search() -> None:
    assert SettingsModel.from_env(HOUSE, search_enabled=True, environ={}).search_enabled is True


def test_data_lake_location_comes_from_the_dataset_profile() -> None:
    settings = SettingsModel.from_env(ONLINE_SHOPPING, environ={"ML_PLATFORM_DATALAKE_ENDPOINT": "http://lake:9000"})

    assert settings.data_lake.endpoint == "http://lake:9000"
    assert settings.data_lake.bucket_name == "online-shopping"
    assert settings.data_lake.object_prefix == "enriched/online_shopping/"
