from datetime import UTC
from datetime import datetime
from enum import StrEnum

from config.settings import settings as main_settings
from keys import Key

class DatalakeEnv(StrEnum):
    RAW = "raw"
    CLEANED = "cleaned"
    ENRICHED = "enriched"


def generate_relative_path(
        env: DatalakeEnv,
        ingestion_time: datetime | None = None,
        dataset_name: str | None = None
) -> str:
    if ingestion_time is None:
        ingestion_time = datetime.now(UTC)

    if dataset_name is None:
        dataset_name = main_settings.app.dataset_name.lower()

    ingestion_id = ingestion_time.strftime("%Y%m%dT%H%M%S%fZ")

    return (
        f"{main_settings.datalake[Key.DATA_PLATFORM_DATALAKE].environment}/{env.value}/{dataset_name.lower()}/"
        f"ingestion_year={ingestion_time.year}/"
        f"ingestion_month={ingestion_time.month:02d}/"
        f"ingestion_day={ingestion_time.day:02d}/"
        f"ingestion_time={ingestion_id}"
    )


def generate_full_path(bucket_name: str, relative_path: str) -> str:
    return f"{main_settings.datalake[Key.DATA_PLATFORM_DATALAKE].scheme}://{bucket_name.strip()}/{relative_path.strip('/')}"
