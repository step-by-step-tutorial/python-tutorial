from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC
from datetime import datetime
from enum import StrEnum

from pyspark.sql import DataFrame

from app_config import env_config as ec


class DatalakeLayer(StrEnum):
    RAW = "raw"
    CLEANED = "cleaned"
    ENRICHED = "enriched"


def build_datalake_path(layer: DatalakeLayer, ingestion_time: datetime | None = None) -> str:
    resolved_ingestion_time = ingestion_time or datetime.now(UTC)

    return (
        f"{ec.DATALAKE_ENVIRONMENT}/{layer.value}/{ec.DATALAKE_SALE_DATASET}/"
        f"ingestion_year={resolved_ingestion_time.year}/"
        f"ingestion_month={resolved_ingestion_time.month:02d}/"
        f"ingestion_day={resolved_ingestion_time.day:02d}"
    )


def build_audit_datalake_uri(object_key: str) -> str:
    return f"s3://{ec.DATALAKE_AUDIT_BUCKET_NAME}/{object_key}"


def build_datalake_uri(path: str) -> str:
    return f"s3://{ec.DATALAKE_BUCKET_NAME}/{path.strip('/')}"


@contextmanager
def persisted_dataframes() -> Iterator[list[DataFrame]]:
    dataframes: list[DataFrame] = []

    try:
        yield dataframes
    finally:
        for dataframe in reversed(dataframes):
            dataframe.unpersist()
