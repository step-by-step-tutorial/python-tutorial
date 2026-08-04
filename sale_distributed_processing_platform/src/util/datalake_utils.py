from datetime import UTC, datetime
from enum import StrEnum

from app_config import env_config as ec


class DatalakeLayer(StrEnum):
    RAW = "raw"
    CLEANED = "cleaned"
    ENRICHED = "enriched"


def build_sale_datalake_path(layer: DatalakeLayer, ingestion_time: datetime | None = None) -> str:
    resolved_ingestion_time = ingestion_time or datetime.now(UTC)

    return (
        f"{ec.DATALAKE_ENVIRONMENT}/{layer.value}/{ec.DATALAKE_SALE_DATASET}/"
        f"ingestion_year={resolved_ingestion_time.year}/"
        f"ingestion_month={resolved_ingestion_time.month:02d}/"
        f"ingestion_day={resolved_ingestion_time.day:02d}"
    )
