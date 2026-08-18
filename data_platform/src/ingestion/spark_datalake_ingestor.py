from __future__ import annotations

import logging

from pyspark.sql import DataFrame, SparkSession

from dataset.definition import DataLakeEndpoint

logger = logging.getLogger(__name__)


class SparkDataLakeIngestor:
    def __init__(self, endpoint: DataLakeEndpoint, session: SparkSession) -> None:
        self.endpoint = endpoint
        self.session = session

    def ingest(self, relative_path: str) -> DataFrame:
        if not relative_path:
            raise ValueError("relative_path is required")

        logger.info("Reading data from %s", relative_path)
        return (
            self.session
            .read
            .parquet(
                f"{self.endpoint.scheme}://"
                f"{self.endpoint.bucket_name.strip()}/"
                f"{relative_path.strip('/')}"
            )
        )
