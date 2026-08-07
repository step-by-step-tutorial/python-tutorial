import logging
from datetime import datetime

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as sf
from pyspark.sql.types import StructType

from app_config import env_config as ec
from app_config.dataframe_schema import DATA_REQUIRED_COLUMNS
from service import (
    spark_sale_service,
)
from service.datalake import datalake_spark_sale_service
from util.datalake_utils import DatalakeLayer, build_datalake_path
from util.spark_dataframe_utils import requires_column
from util.string_utils import should_be_not_none

logger = logging.getLogger(__name__)


def read_stream(session: SparkSession) -> DataFrame:
    should_be_not_none(session, "Spark session")

    return (
        session.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", ec.STREAMING_BOOTSTRAP_SERVERS)
        .option("subscribe", ec.STREAMING_TOPIC)
        .option("startingOffsets", ec.STREAMING_STARTING_OFFSETS)
        .option("failOnDataLoss", "false")
        .load()
    )


def convert(dataframe: DataFrame, schema: StructType) -> DataFrame:
    should_be_not_none(dataframe, "Spark dataFrame")

    new_dataframe = (
        dataframe
        .select(
            sf.from_json(sf.col("value").cast("string"), schema).alias("event"),
            sf.col("topic").alias("kafka_topic"),
            sf.col("partition").alias("kafka_partition"),
            sf.col("offset").alias("kafka_offset"),
            sf.col("timestamp").alias("kafka_timestamp"),
        )
        .filter(sf.col("event").isNotNull())
        .select(
            "event.*",
            "kafka_topic",
            "kafka_partition",
            "kafka_offset",
            "kafka_timestamp",
        )
    )

    requires_column(new_dataframe, DATA_REQUIRED_COLUMNS)

    return new_dataframe


def append_raw_data(df: DataFrame, ingestion_time: datetime) -> DataFrame:
    dataframe = df.drop("kafka_topic", "kafka_partition", "kafka_offset", "kafka_timestamp")
    path = build_datalake_path(layer=DatalakeLayer.RAW, ingestion_time=ingestion_time)
    logger.info("Appending raw data to %s", path)
    datalake_spark_sale_service.append(
        dataframe=dataframe.coalesce(1),
        bucket_name=ec.DATALAKE_BUCKET_NAME,
        path=path
    )
    return dataframe


def append_cleaned_data(df: DataFrame, ingestion_time: datetime) -> DataFrame:
    dataframe = spark_sale_service.clean_data(df)
    path = build_datalake_path(layer=DatalakeLayer.CLEANED, ingestion_time=ingestion_time)
    logger.info("Appending cleaned data to %s", path)
    datalake_spark_sale_service.append(
        dataframe=dataframe.coalesce(1),
        bucket_name=ec.DATALAKE_BUCKET_NAME,
        path=path
    )
    return dataframe


def append_enriched_data(df: DataFrame, ingestion_time: datetime) -> DataFrame:
    dataframe = spark_sale_service.enrich_data(df)
    path = build_datalake_path(layer=DatalakeLayer.ENRICHED, ingestion_time=ingestion_time)
    logger.info("Appending enriched data to %s", path)
    datalake_spark_sale_service.append(
        dataframe=dataframe.coalesce(1),
        bucket_name=ec.DATALAKE_BUCKET_NAME,
        path=path
    )
    return dataframe
