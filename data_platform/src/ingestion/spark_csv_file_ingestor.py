from __future__ import annotations

from pathlib import Path
from typing import Any

from pyspark.sql import DataFrame
from pyspark.sql import SparkSession

from util.string_utils import should_not_be_none, should_not_be_none_or_empty


class SparkCsvFileIngestor:
    def __init__(self, session: SparkSession) -> None:
        self.session = session

    def ingest(self, file_path: str | Path, schema: Any) -> DataFrame:
        should_not_be_none_or_empty(str(file_path), "file_path")
        should_not_be_none(schema, "schema")
        return (
            self.session
            .read
            .option("header", "true")
            .schema(schema)
            .csv(str(file_path))
        )
