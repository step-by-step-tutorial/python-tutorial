from __future__ import annotations

import logging

from pyspark.sql import DataFrame

from connector.session import create_session
from dataset.definition import DataLakeEndpoint

logger = logging.getLogger(__name__)


class SparkDataLakeIngestor:
    def __init__(self, endpoint: DataLakeEndpoint) -> None:
        self.endpoint = endpoint
        self.session = create_session()

    def ingest(self) -> DataFrame:
        if not self.endpoint.relative_path:
            raise ValueError("relative_path is required")

        logger.info("Reading data from %s", self.endpoint.relative_path)
        return (
            self.session
            .read
            .parquet(
                f"{self.endpoint.scheme}://"
                f"{self.endpoint.bucket_name.strip()}/"
                f"{self.endpoint.relative_path.strip('/')}"
            )
        )
