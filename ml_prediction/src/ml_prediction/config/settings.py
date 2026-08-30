import os
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from ml_prediction.config.dataset_profiles import DATASET_PROFILES
from ml_prediction.config.settings_types import TaskType

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class DatasetSource(StrEnum):
    LOCAL = "local"
    DOWNLOAD = "download"


@dataclass(frozen=True)
class DataLakeSettings:
    endpoint: str
    access_key: str
    secret_key: str
    bucket_name: str
    object_prefix: str


@dataclass(frozen=True)
class AppSettings:
    data_dir: Path
    model_dir: Path
    target_column: str
    validation_size: float
    test_size: float
    random_state: int
    data_lake: DataLakeSettings
    task_type: TaskType = TaskType.REGRESSION
    model_type: str = "random_forest"
    n_estimators: int = 200
    n_jobs: int = -1
    max_depth: int | None = None
    min_samples_split: int = 2
    min_samples_leaf: int = 1
    max_features: int | float | str | None = 1.0
    bootstrap: bool = True
    dataset_source: DatasetSource = DatasetSource.LOCAL
    report_dir: Path = PROJECT_ROOT / "reports"
    dataset_name: str = ""
    dataset_filename: str = ""
    model_filename: str = ""
    prediction_filename: str = ""
    prediction_column: str = ""


def load_settings(dataset_name: str) -> AppSettings:
    environment = os.environ
    profile = DATASET_PROFILES[dataset_name]

    return AppSettings(
        data_dir=Path(environment.get("ML_PREDICTION_DATA_DIR", str(PROJECT_ROOT / "data"))),
        model_dir=Path(environment.get("ML_PREDICTION_MODEL_DIR", str(PROJECT_ROOT / "models"))),
        target_column=environment.get("ML_PREDICTION_TARGET_COLUMN", profile.target_column),
        validation_size=float(environment.get("ML_PREDICTION_VALIDATION_SIZE", "0.2")),
        test_size=float(environment.get("ML_PREDICTION_TEST_SIZE", "0.2")),
        random_state=int(environment.get("ML_PREDICTION_RANDOM_STATE", "42")),
        data_lake=DataLakeSettings(
            endpoint=environment.get("ML_PREDICTION_DATALAKE_ENDPOINT", "http://localhost:9000"),
            access_key=environment.get("ML_PREDICTION_DATALAKE_ACCESS_KEY", "admin"),
            secret_key=environment.get("ML_PREDICTION_DATALAKE_SECRET_KEY", "administrator"),
            bucket_name=environment.get("ML_PREDICTION_DATALAKE_BUCKET_NAME", profile.data_lake_bucket),
            object_prefix=environment.get("ML_PREDICTION_DATALAKE_PREFIX", profile.data_lake_prefix),
        ),
        task_type=TaskType(environment.get("ML_PREDICTION_TASK_TYPE", profile.task_type)),
        model_type=environment.get("ML_PREDICTION_MODEL_TYPE", "random_forest"),
        n_estimators=int(environment.get("ML_PREDICTION_N_ESTIMATORS", "200")),
        n_jobs=int(environment.get("ML_PREDICTION_N_JOBS", "-1")),
        max_depth=int(environment.get("ML_PREDICTION_MAX_DEPTH", "0")) or None,
        min_samples_split=int(environment.get("ML_PREDICTION_MIN_SAMPLES_SPLIT", "2")),
        min_samples_leaf=int(environment.get("ML_PREDICTION_MIN_SAMPLES_LEAF", "1")),
        max_features=float(environment.get("ML_PREDICTION_MAX_FEATURES", "1.0")),
        bootstrap=bool(environment.get("ML_PREDICTION_BOOTSTRAP", "True")),
        dataset_source=DatasetSource(environment.get("ML_PREDICTION_DATASET_SOURCE", DatasetSource.LOCAL)),
        report_dir=Path(environment.get("ML_PREDICTION_REPORT_DIR", str(PROJECT_ROOT / "reports"))),
        dataset_name=dataset_name,
        dataset_filename=environment.get("ML_PREDICTION_DATASET_FILENAME", profile.dataset_filename),
        model_filename=environment.get("ML_PREDICTION_MODEL_FILENAME", profile.model_filename),
        prediction_filename=environment.get("ML_PREDICTION_PREDICTION_FILENAME", profile.prediction_filename),
        prediction_column=environment.get("ML_PREDICTION_PREDICTION_COLUMN", profile.prediction_column),
    )


DATASET_SETTINGS: dict[str, AppSettings] = {
    "house": load_settings("house"),
    "online_shopping": load_settings("online_shopping"),
}


def get_settings(dataset_name: str) -> AppSettings:
    return load_settings(dataset_name)
