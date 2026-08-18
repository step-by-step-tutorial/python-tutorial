from __future__ import annotations

from pyspark.sql import DataFrame

from service.spark_service import SparkService


class AuditStreamingChannelIngestor:
    def __init__(self, spark: SparkService) -> None:
        self.spark = spark

    def ingest(self) -> DataFrame:
        return self.spark.read_from_kafka()
