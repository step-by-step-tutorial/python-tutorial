import os
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

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
    dataset_source: DatasetSource = DatasetSource.LOCAL


house_settings = AppSettings(
    data_dir=Path(os.getenv("ML_PREDICTION_DATA_DIR", PROJECT_ROOT / "data")),
    model_dir=Path(os.getenv("ML_PREDICTION_MODEL_DIR", PROJECT_ROOT / "models")),
    target_column=os.getenv("ML_PREDICTION_TARGET_COLUMN", "total_price"),
    validation_size=float(os.getenv("ML_PREDICTION_VALIDATION_SIZE", "0.2")),
    test_size=float(os.getenv("ML_PREDICTION_TEST_SIZE", "0.2")),
    random_state=int(os.getenv("ML_PREDICTION_RANDOM_STATE", "42")),
    dataset_source=DatasetSource(os.getenv("ML_PREDICTION_DATASET_SOURCE", DatasetSource.LOCAL)),
    data_lake=DataLakeSettings(
        endpoint=os.getenv("ML_PREDICTION_DATALAKE_ENDPOINT", "http://localhost:9000"),
        access_key=os.getenv("ML_PREDICTION_DATALAKE_ACCESS_KEY", "admin"),
        secret_key=os.getenv("ML_PREDICTION_DATALAKE_SECRET_KEY", "administrator"),
        bucket_name=os.getenv("ML_PREDICTION_HOUSE_DATALAKE_BUCKET_NAME", "house"),
        object_prefix=os.getenv("ML_PREDICTION_HOUSE_DATALAKE_PREFIX", "house/"),
    ),
)
