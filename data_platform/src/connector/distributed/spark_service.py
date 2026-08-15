from __future__ import annotations

from pyspark.sql import functions as sf

from connector import spark as spark_connection_factory
from config.datalake import settings as datalake_settings
from config.messaging import settings as messaging_settings
from service.spark.batch_service import SparkBatchService
from transformation.validation.schema_validator import requires_column


spark_connection_factory = spark_connection_factory


class SparkService(SparkBatchService):
    def __init__(self, ds) -> None:
        super().__init__()
        self.dataset = ds

    @property
    def session(self):
        if self._session is None:
            self._session = spark_connection_factory.create_connection()
        return self._session

    def read_csv(self, file_path, schema):
        dataframe = super().read_csv(file_path=file_path, schema=schema)
        requires_column(dataframe, self.dataset.required_columns)
        return dataframe

    def read_stream(self, topic: str):
        return super().read_stream(
            topic=topic,
            bootstrap_servers=messaging_settings.bootstrap_servers,
            starting_offsets=messaging_settings.starting_offsets,
        )

    def convert_stream(self, dataframe, schema, required_columns):
        converted = (
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
        requires_column(converted, required_columns)
        return converted

    def read(self, bucket_name: str, path: str):
        return super().read(bucket_name, path, datalake_settings.scheme)

    def overwrite(self, dataframe, bucket_name: str, path: str):
        super().overwrite(dataframe, bucket_name, path, datalake_settings.scheme)

    def append(self, dataframe, bucket_name: str, path: str):
        super().append(dataframe, bucket_name, path, datalake_settings.scheme)
