import logging

from pyspark.sql import DataFrame, SparkSession

from data_platform.model import DataLakeEndpoint, MessagingEndpoint
from data_platform.util.kafka_admin import ensure_topic_exists
from data_platform.util.path_utils import generate_data_lake_path
from data_platform.util.spark_utils import persisted_dataframes
from data_platform.util.string_utils import should_not_be_none, should_not_be_none_or_empty

logger = logging.getLogger(__name__)


class SparkStreamingService:
    def __init__(
            self,
            session: SparkSession,
            messaging_endpoint: MessagingEndpoint,
            data_lake_endpoint: DataLakeEndpoint,
    ) -> None:
        self.session = session
        self.messaging_endpoint = messaging_endpoint
        self.data_lake_endpoint = data_lake_endpoint

    def read_from_kafka(self) -> DataFrame:
        ensure_topic_exists(self.messaging_endpoint.bootstrap_servers, self.messaging_endpoint.channel_name)
        logger.info("Reading data from Kafka topic %s", self.messaging_endpoint.channel_name)
        return (
            self.session.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", self.messaging_endpoint.bootstrap_servers)
            .option("subscribe", self.messaging_endpoint.channel_name)
            .option("startingOffsets", self.messaging_endpoint.starting_offsets)
            .option("failOnDataLoss", "false")
            .load()
        )

    def append_stream_to_object_storage(self, dataframe: DataFrame, path: str, checkpoint_path: str) -> None:
        should_not_be_none(dataframe, "dataframe")
        should_not_be_none_or_empty(path, "path")
        should_not_be_none_or_empty(checkpoint_path, "checkpoint_path")
        logger.info("Writing streaming data to %s", path)

        query = (
            dataframe.writeStream
            .foreachBatch(lambda batch, _: self.append_batch_to_object_storage(batch, path))
            .option("checkpointLocation", checkpoint_path)
            .trigger(availableNow=True)
            .start()
        )
        query.awaitTermination()

    def append_batch_to_object_storage(self, dataframe: DataFrame, path: str) -> None:
        should_not_be_none(dataframe, "dataframe")
        should_not_be_none_or_empty(path, "path")
        logger.info("Appending batch data to %s", path)

        with persisted_dataframes() as persisted:
            if dataframe.isEmpty():
                return
            batch_dataframe = dataframe.persist()
            persisted.append(batch_dataframe)
            batch_dataframe.write.mode("append").parquet(generate_data_lake_path(self.data_lake_endpoint, path))
