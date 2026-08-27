import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


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


settings = AppSettings(
    data_dir=Path(os.getenv("HOUSE_ML_DATA_DIR", PROJECT_ROOT / "data")),
    model_dir=Path(os.getenv("HOUSE_ML_MODEL_DIR", PROJECT_ROOT / "models")),
    target_column=os.getenv("HOUSE_ML_TARGET_COLUMN", "total_price"),
    validation_size=float(os.getenv("HOUSE_ML_VALIDATION_SIZE", "0.2")),
    test_size=float(os.getenv("HOUSE_ML_TEST_SIZE", "0.2")),
    random_state=int(os.getenv("HOUSE_ML_RANDOM_STATE", "42")),
    data_lake=DataLakeSettings(
        endpoint=os.getenv("DATA_PLATFORM_HOUSE_DATALAKE_ENDPOINT", "http://localhost:9000"),
        access_key=os.getenv("DATA_PLATFORM_HOUSE_DATALAKE_ACCESS_KEY", "admin"),
        secret_key=os.getenv("DATA_PLATFORM_HOUSE_DATALAKE_SECRET_KEY", "administrator"),
        bucket_name=os.getenv("DATA_PLATFORM_HOUSE_DATALAKE_BUCKET_NAME", "house"),
        object_prefix=os.getenv("HOUSE_ML_DATALAKE_PREFIX", ""),
    ),
)
