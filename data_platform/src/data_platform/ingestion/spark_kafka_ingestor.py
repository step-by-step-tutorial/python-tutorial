import logging

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as sf
from pyspark.sql.types import StructType

from data_platform.model.endpoints import MessagingEndpoint
from data_platform.util.kafka_admin import ensure_topic_exists

logger = logging.getLogger(__name__)


class SparkKafkaIngestor:
    def __init__(self, endpoint: MessagingEndpoint, session: SparkSession, schema: StructType) -> None:
        self._endpoint = endpoint
        self._session = session
        self._schema = schema

    def ingest(self) -> DataFrame:
        ensure_topic_exists(self._endpoint.bootstrap_servers, self._endpoint.channel_name)
        logger.info("Reading data from Kafka topic %s", self._endpoint.channel_name)
        return (
            self._session
            .readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", self._endpoint.bootstrap_servers)
            .option("subscribe", self._endpoint.channel_name)
            .option("startingOffsets", self._endpoint.starting_offsets)
            .option("failOnDataLoss", "false")
            .load()
            .select(
                sf.from_json(sf.col("value").cast("string"), self._schema).alias("payload")
            )
            .select("payload.*")
        )

