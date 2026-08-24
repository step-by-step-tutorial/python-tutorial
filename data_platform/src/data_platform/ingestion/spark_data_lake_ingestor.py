import logging

from pyspark.sql import DataFrame, SparkSession

from data_platform.model import DataLakeEndpoint
from data_platform.util.string_utils import should_not_be_none_or_empty

logger = logging.getLogger(__name__)


class SparkDataLakeIngestor:
    def __init__(self, endpoint: DataLakeEndpoint, session: SparkSession) -> None:
        self._endpoint = endpoint
        self._session = session

    def ingest(self, relative_path: str) -> DataFrame:
        should_not_be_none_or_empty(relative_path, "relative_path")

        logger.info("Reading data from %s", relative_path)
        return (
            self._session
            .read
            .parquet(
                f"{self._endpoint.scheme}://"
                f"{self._endpoint.bucket_name.strip()}/"
                f"{relative_path.strip('/')}"
            )
        )

