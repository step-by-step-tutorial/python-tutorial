from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeVar

from processor.base import DataProcessor

DataFrameType = TypeVar("DataFrameType")


@dataclass(frozen=True)
class Dataframe:
    schema: Any = None
    required_columns: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Event:
    converter: Callable[[dict[str, str]], dict[str, Any]] | None = None
    key_column: str = ""


@dataclass(frozen=True)
class Messaging:
    server: str = ""
    bootstrap_servers: str = ""
    topic: str = ""
    checkpoint_path: str = ""
    starting_offsets: str = "earliest"


@dataclass(frozen=True)
class Audit:
    topic: str = ""
    archive_enabled: bool = True


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
class DatabaseEndpoint:
    connection: DatabaseConnection = field(default_factory=DatabaseConnection)
    table_name: str = ""
    before_load_sql_files: tuple[str, ...] = ()
    after_load_sql_files: tuple[str, ...] = ()


@dataclass(frozen=True)
class StageDatabase(DatabaseEndpoint):
    pass


@dataclass(frozen=True)
class Datalake:
    bucket_name: str = ""


@dataclass(frozen=True)
class DataWarehouse(DatabaseEndpoint):
    full_table_name: str = ""
    preparing_sql_files: Mapping[str, str] = field(default_factory=dict)
    analysis_sql_files: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class EndpointCatalog:
    file: FileSource = field(default_factory=FileSource)
    database: DatabaseEndpoint = field(default_factory=DatabaseEndpoint)
    datalake: Datalake = field(default_factory=Datalake)
    datawarehouse: DataWarehouse = field(default_factory=DataWarehouse)
    messaging: Messaging = field(default_factory=Messaging)


Source = EndpointCatalog
Destination = EndpointCatalog
Streaming = Messaging


@dataclass(frozen=True)
class Dataset:
    name: str
    dataframe: Dataframe = field(default_factory=Dataframe)
    event: Event = field(default_factory=Event)
    messaging: Messaging = field(default_factory=Messaging)
    audit: Audit = field(default_factory=Audit)
    processors: dict[str, DataProcessor] = field(default_factory=dict)
    source: Source = field(default_factory=Source)
    destination: Destination = field(default_factory=Destination)

    @property
    def dataframe_schema(self) -> Any:
        return self.dataframe.schema

    @property
    def required_columns(self) -> frozenset[str]:
        return self.dataframe.required_columns

    @property
    def event_converter(self) -> Callable[[dict[str, str]], dict[str, Any]] | None:
        return self.event.converter

    @property
    def event_key_column(self) -> str:
        return self.event.key_column

    @property
    def serialization(self) -> Event:
        return self.event

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
    def database(self) -> DatabaseEndpoint:
        return self.destination.database

    @property
    def table_name(self) -> str:
        return self.database.table_name

    @property
    def datawarehouse(self) -> DataWarehouse:
        return self.destination.datawarehouse

    @property
    def streaming(self) -> Messaging:
        return self.messaging

    @property
    def streaming_topic(self) -> str:
        return self.messaging.topic

    @property
    def streaming_checkpoint_path(self) -> str:
        return self.messaging.checkpoint_path

    @property
    def audit_topic(self) -> str:
        return self.audit.topic
