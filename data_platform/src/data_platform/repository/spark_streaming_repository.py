import logging

from pyspark.sql import DataFrame, SparkSession
from data_platform.model.endpoints import DataLakeEndpoint, MessagingEndpoint
from data_platform.repository.spark_datalake_repository import SparkDatalakeRepository
from data_platform.util.kafka_admin import ensure_topic_exists
from data_platform.util.string_utils import should_not_be_none

logger = logging.getLogger(__name__)


class SparkStreamingRepository:
    def __init__(self, session: SparkSession, messaging_endpoint: MessagingEndpoint, data_lake_endpoint: DataLakeEndpoint) -> None:
        self._session = session
        self._messaging_endpoint = messaging_endpoint
        self._datalake_repository = SparkDatalakeRepository(session, data_lake_endpoint)

    def read(self) -> DataFrame:
        ensure_topic_exists(self._messaging_endpoint.bootstrap_servers, self._messaging_endpoint.channel_name)
        endpoint = self._messaging_endpoint
        return (
            self._session.readStream.format("kafka")
            .option("kafka.bootstrap.servers", endpoint.bootstrap_servers)
            .option("subscribe", endpoint.channel_name)
            .option("startingOffsets", endpoint.starting_offsets)
            .option("failOnDataLoss", "false")
            .load()
        )

    def write(self, dataframe: DataFrame, path: str, checkpoint_path: str) -> None:
        should_not_be_none(dataframe, "dataframe")
        query = (
            dataframe.writeStream.foreachBatch(lambda batch, _: self.write_batch(batch, path))
            .option("checkpointLocation", checkpoint_path)
            .trigger(availableNow=True)
            .start()
        )
        query.awaitTermination()

    def write_batch(self, dataframe: DataFrame, path: str) -> None:
        self._datalake_repository.write_batch(dataframe, path)
