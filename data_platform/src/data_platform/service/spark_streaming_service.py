import logging

from pyspark.sql import DataFrame, SparkSession

from data_platform.model.endpoints import MessagingEndpoint, DataLakeEndpoint
from data_platform.util.kafka_admin import ensure_topic_exists
from data_platform.util.path_utils import generate_data_lake_path
from data_platform.util.dataframe_utils import persisted_dataframes
from data_platform.util.string_utils import should_not_be_none, should_not_be_none_or_empty

logger = logging.getLogger(__name__)


class SparkStreamingService:
    def __init__(
            self,
            session: SparkSession,
            messaging_endpoint: MessagingEndpoint,
            data_lake_endpoint: DataLakeEndpoint,
    ) -> None:
        self._session = session
        self._messaging_endpoint = messaging_endpoint
        self._data_lake_endpoint = data_lake_endpoint

    def find(self) -> DataFrame:
        ensure_topic_exists(self._messaging_endpoint.bootstrap_servers, self._messaging_endpoint.channel_name)
        logger.info("Reading data from Kafka topic %s", self._messaging_endpoint.channel_name)
        return (
            self._session.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", self._messaging_endpoint.bootstrap_servers)
            .option("subscribe", self._messaging_endpoint.channel_name)
            .option("startingOffsets", self._messaging_endpoint.starting_offsets)
            .option("failOnDataLoss", "false")
            .load()
        )

    def save_stream(self, dataframe: DataFrame, path: str, checkpoint_path: str) -> None:
        should_not_be_none(dataframe, "dataframe")
        should_not_be_none_or_empty(path, "path")
        should_not_be_none_or_empty(checkpoint_path, "checkpoint_path")
        logger.info("Writing streaming data to %s", path)

        query = (
            dataframe.writeStream
            .foreachBatch(lambda batch, _: self.save_batch(batch, path))
            .option("checkpointLocation", checkpoint_path)
            .trigger(availableNow=True)
            .start()
        )
        query.awaitTermination()

    def save_batch(self, dataframe: DataFrame, path: str) -> None:
        should_not_be_none(dataframe, "dataframe")
        should_not_be_none_or_empty(path, "path")
        logger.info("Appending batch data to %s", path)

        with persisted_dataframes() as persisted:
            if dataframe.isEmpty():
                return
            batch_dataframe = dataframe.persist()
            persisted.append(batch_dataframe)
            batch_dataframe.write.mode("append").parquet(generate_data_lake_path(self._data_lake_endpoint, path))

