from __future__ import annotations

import logging

from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType

from dataset.definition import DataLakeEndpoint, MessagingEndpoint
from service.runtime import persisted_dataframes
from util.string_utils import should_not_be_none, should_not_be_none_or_empty

logger = logging.getLogger(__name__)


class SparkService:
    def __init__(
            self,
            session: SparkSession,
            datalake_endpoint: DataLakeEndpoint,
            messaging_endpoint: MessagingEndpoint
    ) -> None:
        self.session = session
        self.datalake_endpoint = datalake_endpoint
        self.messaging_endpoint = messaging_endpoint

    def read_csv(self, file_path: str, schema: StructType) -> DataFrame:
        should_not_be_none_or_empty(file_path, "file_path")
        should_not_be_none(schema, "schema")
        logger.info(f"Reading data from CSV file {file_path}")
        return (
            self.session
            .read
            .option("header", "true")
            .schema(schema)
            .csv(file_path)
        )

    def read_from_kafka(self) -> DataFrame:
        logger.info(f"Reading data from Kafka topic {self.messaging_endpoint.channel_name}")
        return (
            self.session
            .readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", self.messaging_endpoint.bootstrap_servers)
            .option("subscribe", self.messaging_endpoint.channel_name)
            .option("startingOffsets", self.messaging_endpoint.starting_offsets)
            .option("failOnDataLoss", "false")
            .load()
        )

    def read_from_object_storage(self, path: str) -> DataFrame:
        should_not_be_none_or_empty(path, "path")
        logger.info("Reading data from %s", path)
        return (
            self.session
            .read
            .parquet(
                f"{self.datalake_endpoint.scheme}://"
                f"{self.datalake_endpoint.bucket_name.strip()}/"
                f"{path.strip('/')}"
            )
        )

    def overwrite_to_object_storage(self, dataframe: DataFrame, path: str) -> None:
        should_not_be_none(dataframe, "dataframe")
        should_not_be_none_or_empty(path, "path")
        logger.info("Overwriting data in %s", path)
        (
            dataframe
            .write
            .mode("overwrite")
            .parquet(
                f"{self.datalake_endpoint.scheme}://"
                f"{self.datalake_endpoint.bucket_name.strip()}/"
                f"{path.strip('/')}"
            )
        )

    def append_to_object_storage(self, dataframe: DataFrame, path: str) -> None:
        should_not_be_none(dataframe, "dataframe")
        should_not_be_none_or_empty(path, "path")
        logger.info("Appending data to %s", path)
        (
            dataframe
            .write
            .mode("append")
            .parquet(
                f"{self.datalake_endpoint.scheme}://"
                f"{self.datalake_endpoint.bucket_name.strip()}"
                f"/{path.strip('/')}"
            )
        )

    def append_batch_to_object_storage(self, dataframe: DataFrame, path: str) -> None:
        should_not_be_none(dataframe, "dataframe")
        should_not_be_none_or_empty(path, "path")
        logger.info("Appending batch data to %s", path)

        with persisted_dataframes() as persisted:
            if dataframe.isEmpty():
                return
            batch_dataframe = dataframe.persist()
            persisted.append(batch_dataframe)
            self.append_to_object_storage(dataframe=batch_dataframe, path=path)

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

    def stop(self) -> None:
        logger.info("Stopping Spark session")
        self.session.stop()
