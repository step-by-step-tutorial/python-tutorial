import os
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class DatasetSource(StrEnum):
    LOCAL = "local"
    DOWNLOAD = "download"


class TaskType(StrEnum):
    REGRESSION = "regression"
    CLASSIFICATION = "classification"


def _optional_int_from_env(name: str) -> int | None:
    value = os.getenv(name)
    return None if value is None or value.lower() == "none" else int(value)


def _max_features_from_env() -> int | float | str | None:
    value = os.getenv("ML_PREDICTION_MAX_FEATURES", "1.0")
    if value.lower() == "none":
        return None
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def _bool_from_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


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
    dataset_name: str = "house"
    dataset_filename: str = "house.csv"
    model_filename: str = "house_price_model.joblib"
    prediction_filename: str = "house_predictions.csv"
    prediction_column: str = "predicted_total_price"


house_settings = AppSettings(
    data_dir=Path(os.getenv("ML_PREDICTION_DATA_DIR", PROJECT_ROOT / "data")),
    model_dir=Path(os.getenv("ML_PREDICTION_MODEL_DIR", PROJECT_ROOT / "models")),
    target_column=os.getenv("ML_PREDICTION_TARGET_COLUMN", "total_price"),
    validation_size=float(os.getenv("ML_PREDICTION_VALIDATION_SIZE", "0.2")),
    test_size=float(os.getenv("ML_PREDICTION_TEST_SIZE", "0.2")),
    random_state=int(os.getenv("ML_PREDICTION_RANDOM_STATE", "42")),
    task_type=TaskType(os.getenv("ML_PREDICTION_TASK_TYPE", TaskType.REGRESSION)),
    dataset_source=DatasetSource(os.getenv("ML_PREDICTION_DATASET_SOURCE", DatasetSource.LOCAL)),
    model_type=os.getenv("ML_PREDICTION_MODEL_TYPE", "random_forest"),
    n_estimators=int(os.getenv("ML_PREDICTION_N_ESTIMATORS", "200")),
    n_jobs=int(os.getenv("ML_PREDICTION_N_JOBS", "-1")),
    max_depth=_optional_int_from_env("ML_PREDICTION_MAX_DEPTH"),
    min_samples_split=int(os.getenv("ML_PREDICTION_MIN_SAMPLES_SPLIT", "2")),
    min_samples_leaf=int(os.getenv("ML_PREDICTION_MIN_SAMPLES_LEAF", "1")),
    max_features=_max_features_from_env(),
    bootstrap=_bool_from_env("ML_PREDICTION_BOOTSTRAP", True),
    report_dir=Path(os.getenv("ML_PREDICTION_REPORT_DIR", PROJECT_ROOT / "reports")),
    dataset_name=os.getenv("ML_PREDICTION_DATASET_NAME", "house"),
    dataset_filename=os.getenv("ML_PREDICTION_DATASET_FILENAME", "house.csv"),
    model_filename=os.getenv("ML_PREDICTION_MODEL_FILENAME", "house_price_model.joblib"),
    prediction_filename=os.getenv("ML_PREDICTION_PREDICTION_FILENAME", "house_predictions.csv"),
    prediction_column=os.getenv("ML_PREDICTION_PREDICTION_COLUMN", "predicted_total_price"),
    data_lake=DataLakeSettings(
        endpoint=os.getenv("ML_PREDICTION_DATALAKE_ENDPOINT", "http://localhost:9000"),
        access_key=os.getenv("ML_PREDICTION_DATALAKE_ACCESS_KEY", "admin"),
        secret_key=os.getenv("ML_PREDICTION_DATALAKE_SECRET_KEY", "administrator"),
        bucket_name=os.getenv("ML_PREDICTION_HOUSE_DATALAKE_BUCKET_NAME", "house"),
        object_prefix=os.getenv(
            "ML_PREDICTION_HOUSE_DATALAKE_PREFIX",
            f"{os.getenv('ML_PREDICTION_DATALAKE_STAGE', 'enriched')}/"
            f"{os.getenv('ML_PREDICTION_DATASET_NAME', 'house')}/",
        ),
    ),
)


DATASET_SETTINGS: dict[str, AppSettings] = {
    house_settings.dataset_name: house_settings,
}


def get_settings(dataset_name: str) -> AppSettings:
    try:
        return DATASET_SETTINGS[dataset_name]
    except KeyError as error:
        supported = ", ".join(sorted(DATASET_SETTINGS))
        raise ValueError(
            f"Unsupported dataset: {dataset_name}. Supported datasets: {supported}"
        ) from error
