from typing import Any

from pyspark.sql import DataFrame
from pyspark.sql import SparkSession

from data_platform.util.string_utils import should_not_be_none, should_not_be_none_or_empty


class SparkCsvFileIngestor:
    def __init__(self, session: SparkSession) -> None:
        self.session = session

    def ingest(self, file_path: str, schema: Any) -> DataFrame:
        should_not_be_none_or_empty(file_path, "file_path")
        should_not_be_none(schema, "schema")
        file_path = str(file_path)
        return (
            self.session
            .read
            .option("header", "true")
            .schema(schema)
            .csv(file_path)
        )
