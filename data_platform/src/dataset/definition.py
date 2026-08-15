from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Generic, TypeVar

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


class EndpointType(str, Enum):
    FILE = "file"
    DATABASE = "database"
    REST_API = "rest_api"
    DATALAKE = "datalake"
    DATAWAREHOUSE = "datawarehouse"
    MESSAGING = "messaging"


@dataclass(frozen=True)
class Dataframe:
    schema: Any = None
    required_columns: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Serialization:
    event_converter: Callable[[dict[str, str]], dict[str, Any]] | None = None
    event_key_column: str = ""
    schema_version: str = "1"


@dataclass(frozen=True)
class Messaging:
    server: str = ""
    bootstrap_servers: str = ""
    topic: str = ""
    queue: str = ""
    consumer_group: str = ""
    checkpoint_path: str = ""
    starting_offsets: str = "earliest"
    audit_topic: str = ""
    audit_consumer_group: str = ""
    dead_letter_topic: str = ""


@dataclass(frozen=True)
class Audit:
    topic: str = ""
    consumer_group: str = ""
    dead_letter_topic: str = ""
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
    query: str = ""
    columns: tuple[str, ...] = ()
    before_load_sql_files: tuple[str, ...] = ()
    after_load_sql_files: tuple[str, ...] = ()


@dataclass(frozen=True)
class StageDatabase(DatabaseEndpoint):
    pass


@dataclass(frozen=True)
class DatabaseSource(DatabaseEndpoint):
    pass


@dataclass(frozen=True)
class DatabaseDestination(DatabaseEndpoint):
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
    database: DatabaseSource = field(default_factory=DatabaseSource)
    rest_api: RestApiSource = field(default_factory=RestApiSource)
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
    serialization: Serialization = field(default_factory=Serialization)
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
        return self.serialization.event_converter

    @property
    def event_key_column(self) -> str:
        return self.serialization.event_key_column

    @property
    def schema_version(self) -> str:
        return self.serialization.schema_version

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
    def streaming_consumer_group(self) -> str:
        return self.messaging.consumer_group

    @property
    def streaming_checkpoint_path(self) -> str:
        return self.messaging.checkpoint_path

    @property
    def audit_topic(self) -> str:
        return self.audit.topic

    @property
    def audit_consumer_group(self) -> str:
        return self.audit.consumer_group
