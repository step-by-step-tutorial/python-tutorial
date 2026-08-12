from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Generic, Mapping, TypeVar

DataFrameType = TypeVar("DataFrameType")


class DataProcessor(ABC, Generic[DataFrameType]):

    @abstractmethod
    def clean(self, dataframe: DataFrameType) -> DataFrameType:
        pass

    @abstractmethod
    def enrich(self, dataframe: DataFrameType) -> DataFrameType:
        pass

    @abstractmethod
    def analyze(self, dataframe: DataFrameType) -> Mapping[str, DataFrameType]:
        pass


@dataclass(frozen=True)
class StageTable:
    name: str
    columns: tuple[str, ...]
    before_load_sql_files: tuple[str, ...]
    after_load_sql_files: tuple[str, ...]


@dataclass(frozen=True)
class DataWarehouse:
    table_name: str
    full_table_name: str
    columns: tuple[str, ...]
    preparing_sql_files: Mapping[str, str]
    analysis_sql_files: Mapping[str, str]

@dataclass(frozen=True)
class Datalake:
    bucket_name: str


@dataclass(frozen=True)
class Dataset:
    name: str
    file_name: str
    file_path: str
    dataframe_schema: Any
    required_columns: frozenset[str]
    datalake: Datalake
    database: StageTable
    datawarehouse: DataWarehouse
    processors: dict[str, DataProcessor]
    event_converter: Callable[[dict[str, str]], dict[str, Any]]
    event_key_column: str = ""
    streaming_topic: str = ""
    streaming_consumer_group: str = ""
    streaming_checkpoint_path: str = ""
    audit_topic: str = ""
    audit_consumer_group: str = ""
    schema_version: str = "1"
