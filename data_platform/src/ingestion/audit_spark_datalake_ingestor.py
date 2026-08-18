from __future__ import annotations

from pyspark.sql import DataFrame

from service.spark_service import SparkService


class AuditSparkDataLakeIngestor:
    def __init__(self, relative_path: str, spark: SparkService) -> None:
        self.relative_path = relative_path
        self.spark = spark

    def ingest(self) -> DataFrame:
        return self.spark.read_from_object_storage(path=self.relative_path)
