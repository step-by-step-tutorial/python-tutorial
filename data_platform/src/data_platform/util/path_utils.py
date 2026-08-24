from datetime import UTC
from datetime import datetime
from typing import Any

from data_platform.config.data_lake_environment import StorageEnvironment
from data_platform.config.keys import Key
from data_platform.config.main_settings import settings as main_settings
from data_platform.model import DataLakeEndpoint, StorageObject


def generate_relative_path(
        env: StorageEnvironment,
        ingestion_time: datetime | None = None,
        dataset_name: str | None = None
) -> str:
    if ingestion_time is None:
        ingestion_time = datetime.now(UTC)

    if dataset_name is None:
        dataset_name = main_settings.app.dataset_name.lower()

    ingestion_id = ingestion_time.strftime("%Y%m%dT%H%M%S%fZ")

    return (
        f"{main_settings.data_lake[Key.PLATFORM_DATA_LAKE].environment}/{env.value}/{dataset_name.lower()}/"
        f"ingestion_year={ingestion_time.year}/"
        f"ingestion_month={ingestion_time.month:02d}/"
        f"ingestion_day={ingestion_time.day:02d}/"
        f"ingestion_time={ingestion_id}"
    )


def generate_full_path(bucket_name: str, relative_path: str) -> str:
    return f"{main_settings.data_lake[Key.PLATFORM_DATA_LAKE].scheme}://{bucket_name.strip()}/{relative_path.strip('/')}"


def generate_data_lake_path(endpoint: DataLakeEndpoint, relative_path: str) -> str:
    return f"{endpoint.scheme}://{endpoint.bucket_name.strip()}/{relative_path.strip('/')}"


def extract_filename(path: str) -> str:
    return path.rstrip("/").split("/")[-1]


def to_paths(storage_objects) -> tuple[Any, ...]:
    return tuple(storage_object.path for storage_object in storage_objects)

def to_object_storages(paths: tuple[str, ...]) -> tuple[StorageObject, ...]:
        return tuple[StorageObject](StorageObject("storage", path) for path in paths)
