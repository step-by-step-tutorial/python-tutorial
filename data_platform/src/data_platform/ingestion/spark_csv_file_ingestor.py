from typing import Any

from pyspark.sql import DataFrame
from pyspark.sql import SparkSession

from data_platform.util.validation_utils import require_not_none, require_not_empty


class SparkCsvFileIngestor:
    def __init__(self, session: SparkSession) -> None:
        self._session = session

    def ingest(self, file_path: str, schema: Any) -> DataFrame:
        require_not_empty(file_path, "file_path")
        require_not_none(schema, "schema")
        file_path = str(file_path)
        return (
            self._session
            .read
            .option("header", "true")
            .schema(schema)
            .csv(file_path)
        )
