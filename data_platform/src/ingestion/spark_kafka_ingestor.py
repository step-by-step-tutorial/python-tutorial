
import logging

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as sf
from pyspark.sql.types import StructType

from dataset.definition import MessagingEndpoint
from util.kafka_admin import ensure_topic_exists

logger = logging.getLogger(__name__)


class SparkKafkaIngestor:
    def __init__(self, endpoint: MessagingEndpoint, session: SparkSession, schema: StructType) -> None:
        self.endpoint = endpoint
        self.session = session
        self.schema = schema

    def ingest(self) -> DataFrame:
        ensure_topic_exists(self.endpoint.bootstrap_servers, self.endpoint.channel_name)
        logger.info("Reading data from Kafka topic %s", self.endpoint.channel_name)
        return (
            self.session
            .readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", self.endpoint.bootstrap_servers)
            .option("subscribe", self.endpoint.channel_name)
            .option("startingOffsets", self.endpoint.starting_offsets)
            .option("failOnDataLoss", "false")
            .load()
            .select(
                sf.from_json(sf.col("value").cast("string"), self.schema).alias("payload")
            )
            .select("payload.*")
        )
