import logging

from pyspark.sql import DataFrame, SparkSession

from data_platform.model.endpoints import DataLakeEndpoint
from data_platform.repository.storage_repository import StorageRepository
from data_platform.util.dataframe_utils import persisted_dataframes
from data_platform.util.path_utils import generate_datalake_path
from data_platform.util.string_utils import should_not_be_none, should_not_be_none_or_empty

logger = logging.getLogger(__name__)


class SparkDatalakeRepository(StorageRepository):
    def __init__(self, session: SparkSession, datalake_endpoint: DataLakeEndpoint) -> None:
        self._session = session
        self._datalake_endpoint = datalake_endpoint

    def read(self, path: str) -> DataFrame:
        should_not_be_none_or_empty(path, "path")
        logger.info("Reading Spark datalake data: bucket=%s path=%s", self._datalake_endpoint.bucket_name, path)
        return self._session.read.parquet(generate_datalake_path(self._datalake_endpoint, path))

    def write(self, dataframe: DataFrame, path: str) -> str:
        should_not_be_none(dataframe, "dataframe")
        should_not_be_none_or_empty(path, "path")
        logger.info("Writing Spark datalake data: bucket=%s path=%s", self._datalake_endpoint.bucket_name, path)
        dataframe.write.mode("append").parquet(generate_datalake_path(self._datalake_endpoint, path))
        return path

    def overwrite(self, dataframe: DataFrame, path: str) -> str:
        should_not_be_none(dataframe, "dataframe")
        should_not_be_none_or_empty(path, "path")
        dataframe.write.mode("overwrite").parquet(generate_datalake_path(self._datalake_endpoint, path))
        return path

    def write_batch(self, dataframe: DataFrame, path: str) -> None:
        should_not_be_none(dataframe, "dataframe")
        should_not_be_none_or_empty(path, "path")
        if dataframe.isEmpty():
            logger.debug("Skipping empty Spark batch: path=%s", path)
            return
        with persisted_dataframes() as persisted:
            batch = dataframe.persist()
            persisted.append(batch)
            self.write(batch, path)
