import logging
import os
import tempfile
from pathlib import Path
from urllib.request import Request, build_opener

from pyspark.sql import DataFrame, SparkSession

from data_platform.model.dataset_ingestor import DatasetIngestor
from data_platform.model.endpoints import RestApiEndpoint
from data_platform.util.string_utils import should_not_be_none

logger = logging.getLogger(__name__)


class SparkRestApiCsvIngestor(DatasetIngestor):
    def __init__(self, endpoint: RestApiEndpoint, session: SparkSession, schema) -> None:
        self._endpoint = endpoint
        self._session = session
        self._schema = schema
        self.name = "spark_api"

    def ingest(self) -> DataFrame:
        should_not_be_none(self._schema, "schema")
        logger.info("Downloading CSV resource into Spark: url=%s", self._endpoint.url)
        request = Request(self._endpoint.url, method=self._endpoint.method, headers=self._endpoint.headers)
        with build_opener().open(request) as response:
            payload = response.read()

        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temporary_file:
                temporary_file.write(payload)
                temporary_path = Path(temporary_file.name)
            dataframe = (
                self._session.read.option("header", "true").schema(self._schema).csv(str(temporary_path))
                .cache()
            )
            row_count = dataframe.count()
            logger.info("Loaded CSV resource into Spark: url=%s rows=%s columns=%s bytes=%s", self._endpoint.url, row_count, len(dataframe.columns), len(payload))
            return dataframe
        finally:
            if temporary_path is not None:
                try:
                    os.unlink(temporary_path)
                except FileNotFoundError:
                    pass
