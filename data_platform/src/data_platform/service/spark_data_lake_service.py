import logging

from pyspark.sql import DataFrame, SparkSession

from data_platform.model import DataLakeEndpoint
from data_platform.util.path_utils import generate_data_lake_path
from data_platform.util.spark_utils import persisted_dataframes
from data_platform.util.string_utils import should_not_be_none, should_not_be_none_or_empty

logger = logging.getLogger(__name__)


class SparkDataLakeService:
    def __init__(self, session: SparkSession, data_lake_endpoint: DataLakeEndpoint) -> None:
        self._session = session
        self._data_lake_endpoint = data_lake_endpoint

    def find(self, path: str) -> DataFrame:
        should_not_be_none_or_empty(path, "path")
        logger.info("Reading data from %s", path)
        return self._session.read.parquet(generate_data_lake_path(self._data_lake_endpoint, path))

    def replace(self, dataframe: DataFrame, path: str) -> None:
        should_not_be_none(dataframe, "dataframe")
        should_not_be_none_or_empty(path, "path")
        logger.info("Overwriting data in %s", path)
        dataframe.write.mode("overwrite").parquet(generate_data_lake_path(self._data_lake_endpoint, path))

    def save(self, dataframe: DataFrame, path: str) -> None:
        should_not_be_none(dataframe, "dataframe")
        should_not_be_none_or_empty(path, "path")
        logger.info("Appending data to %s", path)
        dataframe.write.mode("append").parquet(generate_data_lake_path(self._data_lake_endpoint, path))

    def save_batch(self, dataframe: DataFrame, path: str) -> None:
        should_not_be_none(dataframe, "dataframe")
        should_not_be_none_or_empty(path, "path")
        logger.info("Appending batch data to %s", path)

        with persisted_dataframes() as persisted:
            if dataframe.isEmpty():
                return
            batch_dataframe = dataframe.persist()
            persisted.append(batch_dataframe)
            self.save(dataframe=batch_dataframe, path=path)

