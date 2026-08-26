import logging

from collections.abc import Callable

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as sf
from pyspark.sql.types import StructType

from data_platform.model.dataset_ingestor import DatasetIngestor
from data_platform.model.endpoints import MessagingEndpoint

logger = logging.getLogger(__name__)


class SparkKafkaIngestor(DatasetIngestor):
    def __init__(self, endpoint: MessagingEndpoint, session: SparkSession | Callable[[], SparkSession], schema: StructType) -> None:
        self._endpoint = endpoint
        self._session = session
        self._schema = schema
        self.name = "spark_kafka"

    @property
    def session(self) -> SparkSession:
        if hasattr(self._session, "readStream"):
            return self._session
        self._session = self._session()
        return self._session

    def ingest(self) -> DataFrame:
        logger.info(
            "Reading batch data from Kafka: bootstrap_servers=%s topic=%s starting_offsets=%s",
            self._endpoint.bootstrap_servers,
            self._endpoint.channel_name,
            self._endpoint.starting_offsets,
        )
        return (
            self.session
            .read
            .format("kafka")
            .option("kafka.bootstrap.servers", self._endpoint.bootstrap_servers)
            .option("subscribe", self._endpoint.channel_name)
            .option("startingOffsets", self._endpoint.starting_offsets)
            .option("endingOffsets", "latest")
            .option("failOnDataLoss", "false")
            .load()
            .select(
                sf.from_json(sf.col("value").cast("string"), self._schema).alias("payload")
            )
            .select("payload.*")
        )
