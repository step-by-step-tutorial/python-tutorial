from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Generic, Mapping, TypeVar

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
class FileSource:
    file_name: str = ""
    file_path: str = ""
    file_format: str = "csv"
    encoding: str = "utf-8"

    def resolve_path(self, base_path: str | Path) -> Path:
        if self.file_path:
            return Path(self.file_path)

        if not self.file_name:
            raise ValueError("Cannot resolve file path because file_name is empty.")

        return Path(base_path) / self.file_name


@dataclass(frozen=True)
class DatabaseConnection:
    server: str = ""
    port: int = 0
    database_name: str = ""
    user: str = ""
    password: str = ""
    driver: str = ""
    jdbc_url: str = ""


@dataclass(frozen=True)
class DatabaseSource:
    connection: DatabaseConnection = field(default_factory=DatabaseConnection)
    table_name: str = ""
    query: str = ""
    columns: tuple[str, ...] = ()


@dataclass(frozen=True)
class DatabaseDestination:
    connection: DatabaseConnection = field(default_factory=DatabaseConnection)
    table_name: str = ""
    columns: tuple[str, ...] = ()
    before_load_sql_files: tuple[str, ...] = ()
    after_load_sql_files: tuple[str, ...] = ()


@dataclass(frozen=True)
class StageDatabase(DatabaseDestination):
    pass


@dataclass(frozen=True)
class RestApiSource:
    base_url: str = ""
    endpoint: str = ""
    method: str = "GET"
    headers: Mapping[str, str] = field(default_factory=dict)
    query_params: Mapping[str, str] = field(default_factory=dict)
    timeout_seconds: int = 30


@dataclass(frozen=True)
class TopicSource:
    server: str = ""
    topic: str = ""
    consumer_group: str = ""


@dataclass(frozen=True)
class QueueSource:
    server: str = ""
    queue: str = ""
    consumer_group: str = ""


@dataclass(frozen=True)
class Streaming:
    server: str = ""
    bootstrap_servers: str = ""
    topic: str = ""
    consumer_group: str = ""
    checkpoint_path: str = ""
    starting_offsets: str = "earliest"
    audit_topic: str = ""
    audit_consumer_group: str = ""
    dead_letter_topic: str = ""


@dataclass(frozen=True)
class Source:
    file: FileSource = field(default_factory=FileSource)
    database: DatabaseSource = field(default_factory=DatabaseSource)
    rest_api: RestApiSource = field(default_factory=RestApiSource)
    topic: TopicSource = field(default_factory=TopicSource)
    queue: QueueSource = field(default_factory=QueueSource)


@dataclass(frozen=True)
class Destination:
    database: StageDatabase = field(default_factory=StageDatabase)
    datawarehouse: "DataWarehouse" = field(default_factory=lambda: DataWarehouse())
    datalake: "Datalake" = field(default_factory=lambda: Datalake())
    streaming: Streaming = field(default_factory=Streaming)


@dataclass(frozen=True)
class Datalake:
    bucket_name: str = ""


@dataclass(frozen=True)
class DataWarehouse(DatabaseDestination):
    full_table_name: str = ""
    preparing_sql_files: Mapping[str, str] = field(default_factory=dict)
    analysis_sql_files: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Dataset:
    name: str
    dataframe_schema: Any
    required_columns: frozenset[str]
    processors: dict[str, DataProcessor]
    event_converter: Callable[[dict[str, str]], dict[str, Any]]
    source: Source = field(default_factory=Source)
    destination: Destination = field(default_factory=Destination)
    streaming: Streaming = field(default_factory=Streaming)
    schema_version: str = "1"
    event_key_column: str = ""

    @property
    def file_name(self) -> str:
        return self.source.file.file_name

    @property
    def file_path(self) -> str:
        return self.source.file.file_path

    @property
    def datalake(self) -> Datalake:
        return self.destination.datalake

    @property
    def database(self) -> DatabaseDestination:
        return self.destination.database

    @property
    def table_name(self) -> str:
        return self.database.table_name

    @property
    def datawarehouse(self) -> DataWarehouse:
        return self.destination.datawarehouse

    @property
    def streaming_topic(self) -> str:
        return self.streaming.topic

    @property
    def streaming_consumer_group(self) -> str:
        return self.streaming.consumer_group

    @property
    def streaming_checkpoint_path(self) -> str:
        return self.streaming.checkpoint_path

    @property
    def audit_topic(self) -> str:
        return self.streaming.audit_topic

    @property
    def audit_consumer_group(self) -> str:
        return self.streaming.audit_consumer_group
