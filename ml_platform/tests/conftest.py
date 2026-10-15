from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ml_platform.config.dataset_profiles import HOUSE, ONLINE_SHOPPING
from ml_platform.config.task_type import TaskType
from ml_platform.model.dataset_profile_model import DatasetProfileModel
from ml_platform.model.settings_model import DataLakeSettingsModel, ModelParametersModel, SettingsModel


def make_dataframe(profile: DatasetProfileModel, rows: int = 60, seed: int = 0) -> pd.DataFrame:
    generator = np.random.default_rng(seed)
    features = profile.features
    data: dict[str, object] = {column: generator.uniform(1, 100, rows) for column in features.numeric}
    data |= {column: generator.choice([True, False, "True", "False"], rows) for column in features.boolean}
    data |= {column: generator.choice(["A", "B", "C"], rows) for column in features.categorical}
    dataframe = pd.DataFrame(data)
    first_numeric = dataframe[features.numeric[0]]
    if profile.task_type == TaskType.REGRESSION:
        dataframe[profile.target_column] = first_numeric * 1000
    else:
        dataframe[profile.target_column] = np.where(first_numeric > 50, "Delivered", "Cancelled")
    return dataframe


def make_settings(tmp_path: Path, profile: DatasetProfileModel, **overrides) -> SettingsModel:
    values = {
        "profile": profile,
        "data_dir": tmp_path / "data",
        "model_dir": tmp_path / "models",
        "audit_dir": tmp_path / "audit",
        "output_dir": tmp_path / "output",
        "data_lake": DataLakeSettingsModel("http://localhost:9000", "key", "secret", profile.data_lake_bucket,
                                           profile.data_lake_prefix),
        "model_parameters": ModelParametersModel(n_estimators=10, n_jobs=1),
    }
    return SettingsModel(**(values | overrides))


def write_dataset(settings: SettingsModel, rows: int = 60) -> pd.DataFrame:
    dataframe = make_dataframe(settings.profile, rows)
    settings.dataset_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(settings.dataset_path, index=False)
    return dataframe


@pytest.fixture
def house_settings(tmp_path: Path) -> SettingsModel:
    settings = make_settings(tmp_path, HOUSE)
    write_dataset(settings)
    return settings


@pytest.fixture
def online_shopping_settings(tmp_path: Path) -> SettingsModel:
    settings = make_settings(tmp_path, ONLINE_SHOPPING)
    write_dataset(settings)
    return settings
