from datetime import UTC
from datetime import datetime
from enum import StrEnum

from config.app import settings as app_settings
from config.datalake import settings as datalake_settings


class DatalakeLayer(StrEnum):
    RAW = "raw"
    CLEANED = "cleaned"
    ENRICHED = "enriched"


def generate_relative_path(
        layer: DatalakeLayer,
        ingestion_time: datetime | None = None,
        dataset_name: str | None = None
) -> str:
    if ingestion_time is None:
        ingestion_time = datetime.now(UTC)

    if dataset_name is None:
        dataset_name = app_settings.dataset_name.lower()

    ingestion_id = ingestion_time.strftime("%Y%m%dT%H%M%S%fZ")

    return (
        f"{datalake_settings.environment}/{layer.value}/{dataset_name.lower()}/"
        f"ingestion_year={ingestion_time.year}/"
        f"ingestion_month={ingestion_time.month:02d}/"
        f"ingestion_day={ingestion_time.day:02d}/"
        f"ingestion_time={ingestion_id}"
    )


def generate_full_path(bucket_name: str, relative_path: str) -> str:
    return f"{datalake_settings.scheme}://{bucket_name.strip()}/{relative_path.strip('/')}"


def build_audit_datalake_uri(object_key: str) -> str:
    return generate_full_path(datalake_settings.audit_bucket_name, object_key)


def build_datalake_uri(path: str) -> str:
    return generate_full_path(datalake_settings.bucket_name, path)
