import logging

from pyspark.sql import DataFrame, SparkSession

from data_platform.model.endpoints import DataLakeEndpoint
from data_platform.util.path_utils import generate_datalake_path
from data_platform.util.string_utils import should_not_be_none_or_empty

logger = logging.getLogger(__name__)


class SparkDatalakeIngestor:
    def __init__(self, endpoint: DataLakeEndpoint, session: SparkSession) -> None:
        self._endpoint = endpoint
        self._session = session

    def ingest(self, relative_path: str) -> DataFrame:
        should_not_be_none_or_empty(relative_path, "relative_path")
        logger.info("Reading Spark datalake data: path=%s", relative_path)
        return self._session.read.parquet(generate_datalake_path(self._endpoint, relative_path))
