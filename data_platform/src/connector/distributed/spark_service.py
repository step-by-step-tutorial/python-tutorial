import logging
from collections.abc import Collection

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as sf
from pyspark.sql.types import StructType

from app_config import env_config as ec
from connector.distributed import spark_connector as spark_connection_factory
from dataset.definition import Dataset
from transformation.validation.schema_validator import requires_column
from util.string_utils import should_be_not_none, should_not_be_none_or_empty

logger = logging.getLogger(__name__)


class SparkService:

    def __init__(self, ds: Dataset) -> None:
        self.dataset = ds
        self._session: SparkSession | None = None

    @property
    def session(self) -> SparkSession:
        if self._session is None:
            self._session = spark_connection_factory.create_connection()

        return self._session

    def read_csv(self, file_path: str, schema: StructType) -> DataFrame:
        should_not_be_none_or_empty(file_path, "file_path")
        should_be_not_none(schema, "schema")

        dataframe = (
            self.session.read
            .option("header", "true")
            .schema(schema)
            .csv(file_path)
        )

        requires_column(dataframe, self.dataset.dataframe.required_columns)

        return dataframe

    def read_stream(self, topic: str) -> DataFrame:
        should_not_be_none_or_empty(topic, "topic")

        bootstrap_servers = self.dataset.messaging.bootstrap_servers or self.dataset.messaging.server or ec.APP_STREAMING_BOOTSTRAP_SERVERS

        return (
            self.session.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", bootstrap_servers)
            .option("subscribe", topic)
            .option("startingOffsets", self.dataset.messaging.starting_offsets or ec.APP_STREAMING_STARTING_OFFSETS)
            .option("failOnDataLoss", "false")
            .load()
        )

    def convert_stream(self, dataframe: DataFrame, schema: StructType, required_columns: Collection[str]) -> DataFrame:
        should_be_not_none(dataframe, "dataframe")
        should_be_not_none(schema, "schema")

        converted_dataframe = (
            dataframe
            .select(
                sf.from_json(sf.col("value").cast("string"), schema).alias("event"),
                sf.col("topic").alias("streaming_topic"),
                sf.col("partition").alias("streaming_partition"),
                sf.col("offset").alias("streaming_offset"),
                sf.col("timestamp").alias("streaming_timestamp")
            )
            .filter(sf.col("event").isNotNull())
            .select(
                "event.*",
                "streaming_topic",
                "streaming_partition",
                "streaming_offset",
                "streaming_timestamp"
            )
        )

        requires_column(converted_dataframe, required_columns)

        return converted_dataframe

    def read(self, bucket_name: str, path: str) -> DataFrame:
        should_not_be_none_or_empty(bucket_name, "bucket_name")
        should_not_be_none_or_empty(path, "path")

        logger.info("Reading data from %s", path)

        return self.session.read.parquet(
            f"{ec.APP_DATALAKE_SCHEME}://{bucket_name.strip()}/{path.strip('/')}"
        )

    def overwrite(self, dataframe: DataFrame, bucket_name: str, path: str) -> None:
        should_be_not_none(dataframe, "dataframe")
        should_not_be_none_or_empty(bucket_name, "bucket_name")
        should_not_be_none_or_empty(path, "path")

        logger.info("Overwriting data in %s", path)

        dataframe.write.mode("overwrite").parquet(
            f"{ec.APP_DATALAKE_SCHEME}://{bucket_name.strip()}/{path.strip('/')}"
        )

    def append(self, dataframe: DataFrame, bucket_name: str, path: str) -> None:
        should_be_not_none(dataframe, "dataframe")
        should_not_be_none_or_empty(bucket_name, "bucket_name")
        should_not_be_none_or_empty(path, "path")

        logger.info("Appending data to %s", path)

        dataframe.write.mode("append").parquet(
            f"{ec.APP_DATALAKE_SCHEME}://{bucket_name.strip()}/{path.strip('/')}"
        )

    def stop(self) -> None:
        if self._session is None:
            return

        logger.info("Stopping Spark session")
        self._session.stop()
        self._session = None
