from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as sf

from app_config import env_config as ec
from app_config.dataframe_schema import SCHEMA, SALE_REQUIRED_COLUMNS
from util.spark_dataframe_utils import requires_column


def read_sale_event_stream(session: SparkSession) -> DataFrame:
    if session is None:
        raise ValueError("Cannot read sale events because the Spark session is None.")

    return (
        session.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", ec.KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", ec.KAFKA_TOPIC)
        .option("startingOffsets", ec.KAFKA_STARTING_OFFSETS)
        .option("failOnDataLoss", "false")
        .load()
    )


def parse_sale_event_stream(dataframe: DataFrame) -> DataFrame:
    if dataframe is None:
        raise ValueError("Cannot parse sale events because the input DataFrame is None.")

    parsed_dataframe = (
        dataframe
        .select(
            sf.from_json(sf.col("value").cast("string"), SCHEMA).alias("sale_event"),
            sf.col("topic").alias("kafka_topic"),
            sf.col("partition").alias("kafka_partition"),
            sf.col("offset").alias("kafka_offset"),
            sf.col("timestamp").alias("kafka_timestamp"),
        )
        .filter(sf.col("sale_event").isNotNull())
        .select(
            "sale_event.*",
            "kafka_topic",
            "kafka_partition",
            "kafka_offset",
            "kafka_timestamp",
        )
    )

    requires_column(parsed_dataframe, SALE_REQUIRED_COLUMNS)

    return parsed_dataframe