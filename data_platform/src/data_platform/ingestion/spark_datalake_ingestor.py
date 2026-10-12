import logging

from pyspark.sql import DataFrame, SparkSession

from data_platform.model.endpoint_model import DataLakeEndpointModel
from data_platform.util.validation_utils import require_not_empty

logger = logging.getLogger(__name__)


class SparkDatalakeIngestor:
    def __init__(self, endpoint: DataLakeEndpointModel, session: SparkSession) -> None:
        self._endpoint = endpoint
        self._session = session

    def ingest(self, relative_path: str) -> DataFrame:
        require_not_empty(relative_path, "relative_path")
        logger.info("Reading Spark datalake data: path=%s", relative_path)
        return self._session.read.parquet(self._endpoint.full_path(relative_path))
