from datetime import UTC
from datetime import datetime
from enum import StrEnum

from app_config import env_config as ec


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
        dataset_name = ec.DATASET_NAME.lower()

    ingestion_id = ingestion_time.strftime("%Y%m%dT%H%M%S%fZ")

    return (
        f"{ec.APP_DATALAKE_ENVIRONMENT}/{layer.value}/{dataset_name.lower()}/"
        f"ingestion_year={ingestion_time.year}/"
        f"ingestion_month={ingestion_time.month:02d}/"
        f"ingestion_day={ingestion_time.day:02d}/"
        f"ingestion_time={ingestion_id}"
    )


def generate_full_path(bucket_name: str, relative_path: str) -> str:
    return f"{ec.APP_DATALAKE_SCHEME}://{bucket_name.strip()}/{relative_path.strip('/')}"


def build_audit_datalake_uri(object_key: str) -> str:
    return generate_full_path(ec.APP_DATALAKE_AUDIT_BUCKET_NAME, object_key)


def build_datalake_uri(path: str) -> str:
    return generate_full_path(ec.APP_DATALAKE_BUCKET_NAME, path)
