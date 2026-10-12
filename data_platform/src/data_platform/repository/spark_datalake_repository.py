import logging
from collections.abc import Callable

from pyspark.sql import DataFrame, SparkSession

from data_platform.model.endpoint_model import DataLakeEndpointModel
from data_platform.repository.storage_repository import StorageRepository
from data_platform.util.dataframe_utils import persisted_dataframes
from data_platform.util.validation_utils import require_not_none, require_not_empty

logger = logging.getLogger(__name__)


class SparkDatalakeRepository(StorageRepository):
    def __init__(
            self,
            session: SparkSession | Callable[[], SparkSession],
            datalake_endpoint: DataLakeEndpointModel,
    ) -> None:
        self._session = session
        self._datalake_endpoint = datalake_endpoint

    @property
    def session(self) -> SparkSession:
        if hasattr(self._session, "read"):
            return self._session
        self._session = self._session()
        return self._session

    def read(self, path: str) -> DataFrame:
        require_not_empty(path, "path")
        logger.info("Reading Spark datalake data: bucket=%s path=%s", self._datalake_endpoint.bucket_name, path)
        return self.session.read.parquet(self._datalake_endpoint.full_path(path))

    def write(self, dataframe: DataFrame, path: str) -> str:
        require_not_none(dataframe, "dataframe")
        require_not_empty(path, "path")
        logger.info("Writing Spark datalake data: bucket=%s path=%s", self._datalake_endpoint.bucket_name, path)
        dataframe.write.mode("append").parquet(self._datalake_endpoint.full_path(path))
        return path

    def overwrite(self, dataframe: DataFrame, path: str) -> str:
        require_not_none(dataframe, "dataframe")
        require_not_empty(path, "path")
        dataframe.write.mode("overwrite").parquet(self._datalake_endpoint.full_path(path))
        return path

    def write_batch(self, dataframe: DataFrame, path: str) -> None:
        require_not_none(dataframe, "dataframe")
        require_not_empty(path, "path")
        if dataframe.isEmpty():
            logger.debug("Skipping empty Spark batch: path=%s", path)
            return
        with persisted_dataframes() as persisted:
            batch = dataframe.persist()
            persisted.append(batch)
            self.write(batch, path)
