from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from processor.base import DataProcessor


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
class Messaging:
    server: str = ""
    bootstrap_servers: str = ""
    topic: str = ""
    checkpoint_path: str = ""
    starting_offsets: str = "earliest"


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
class Datalake:
    bucket_name: str = ""


@dataclass(frozen=True)
class StageDatabase:
    connection: DatabaseConnection = field(default_factory=DatabaseConnection)
    table_name: str = ""
    before_load_sql_files: tuple[str, ...] = ()
    after_load_sql_files: tuple[str, ...] = ()


@dataclass(frozen=True)
class DataWarehouse:
    connection: DatabaseConnection = field(default_factory=DatabaseConnection)
    table_name: str = ""
    full_table_name: str = ""
    preparing_sql_files: Mapping[str, str] = field(default_factory=dict)
    analysis_sql_files: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Source:
    file: FileSource = field(default_factory=FileSource)
    messaging: Messaging = field(default_factory=Messaging)


@dataclass(frozen=True)
class Destination:
    datalake: Datalake = field(default_factory=Datalake)
    database: StageDatabase = field(default_factory=StageDatabase)
    datawarehouse: DataWarehouse = field(default_factory=DataWarehouse)
    messaging: Messaging = field(default_factory=Messaging)


@dataclass(frozen=True)
class EndpointView:
    endpoints: Mapping[str, Any] = field(default_factory=dict)

    def __getattr__(self, item: str) -> Any:
        try:
            return self.endpoints[item]
        except KeyError as error:
            raise AttributeError(item) from error

    def __getitem__(self, item: str) -> Any:
        return self.endpoints[item]


@dataclass(frozen=True)
class FileEndpoint:
    name: str = "file"
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
class DatabaseEndpoint:
    name: str = "database"
    table_name: str = ""
    before_load_sql_files: tuple[str, ...] = ()
    after_load_sql_files: tuple[str, ...] = ()


@dataclass(frozen=True)
class DataLakeEndpoint:
    name: str = "datalake"
    bucket_name: str = ""


@dataclass(frozen=True)
class DataWarehouseEndpoint:
    name: str = "datawarehouse"
    table_name: str = ""
    full_table_name: str = ""
    preparing_sql_files: Mapping[str, str] = field(default_factory=dict)
    analysis_sql_files: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class MessagingEndpoint:
    name: str = "messaging"
    topic: str = ""
    server: str = ""
    bootstrap_servers: str = ""
    checkpoint_path: str = ""
    starting_offsets: str = "earliest"


@dataclass(frozen=True, init=False)
class Dataframe:
    _schema: Any = None
    schema_factory: Callable[[], Any] | None = None
    required_columns: frozenset[str] = frozenset()

    def __init__(
        self,
        schema: Any = None,
        required_columns: frozenset[str] = frozenset(),
        schema_factory: Callable[[], Any] | None = None,
    ) -> None:
        object.__setattr__(self, "_schema", schema)
        object.__setattr__(self, "schema_factory", schema_factory)
        object.__setattr__(self, "required_columns", required_columns)

    @property
    def schema(self) -> Any:
        if self.schema_factory is not None:
            return self.schema_factory()
        return self._schema


@dataclass(frozen=True)
class Event:
    converter: Callable[[dict[str, str]], dict[str, Any]] | None = None
    key_column: str = ""


@dataclass(frozen=True)
class Audit:
    topic: str = ""
    archive_enabled: bool = True


class _EndpointType(Protocol):
    name: str


def _source_mapping(source: Source | None, messaging: Messaging | None) -> dict[str, Any]:
    mapping: dict[str, Any] = {}

    if source is not None:
        if source.file.file_name or source.file.file_path:
            mapping["file"] = FileEndpoint(
                name="file",
                file_name=source.file.file_name,
                file_path=source.file.file_path,
                file_format=source.file.file_format,
                encoding=source.file.encoding,
            )

        if source.messaging.topic:
            mapping["messaging"] = MessagingEndpoint(
                name="messaging",
                topic=source.messaging.topic,
                server=source.messaging.server,
                bootstrap_servers=source.messaging.bootstrap_servers,
                checkpoint_path=source.messaging.checkpoint_path,
                starting_offsets=source.messaging.starting_offsets,
            )

    if messaging is not None and messaging.topic and "messaging" not in mapping:
        mapping["messaging"] = MessagingEndpoint(
            name="messaging",
            topic=messaging.topic,
            server=messaging.server,
            bootstrap_servers=messaging.bootstrap_servers,
            checkpoint_path=messaging.checkpoint_path,
            starting_offsets=messaging.starting_offsets,
        )

    return mapping


def _destination_mapping(destination: Destination | None) -> dict[str, Any]:
    mapping: dict[str, Any] = {}

    if destination is None:
        return mapping

    if destination.datalake.bucket_name:
        mapping["datalake"] = DataLakeEndpoint(name="datalake", bucket_name=destination.datalake.bucket_name)

    if destination.database.table_name:
        mapping["database"] = DatabaseEndpoint(
            name="database",
            table_name=destination.database.table_name,
            before_load_sql_files=destination.database.before_load_sql_files,
            after_load_sql_files=destination.database.after_load_sql_files,
        )

    if destination.datawarehouse.full_table_name or destination.datawarehouse.table_name:
        mapping["datawarehouse"] = DataWarehouseEndpoint(
            name="datawarehouse",
            table_name=destination.datawarehouse.table_name,
            full_table_name=destination.datawarehouse.full_table_name,
            preparing_sql_files=destination.datawarehouse.preparing_sql_files,
            analysis_sql_files=destination.datawarehouse.analysis_sql_files,
        )

    if destination.messaging.topic:
        mapping["messaging"] = MessagingEndpoint(
            name="messaging",
            topic=destination.messaging.topic,
            server=destination.messaging.server,
            bootstrap_servers=destination.messaging.bootstrap_servers,
            checkpoint_path=destination.messaging.checkpoint_path,
            starting_offsets=destination.messaging.starting_offsets,
        )

    return mapping


@dataclass(frozen=True, init=False)
class Dataset:
    name: str
    dataframe: Dataframe
    event: Event
    audit: Audit
    processors: Mapping[str, DataProcessor]
    sources: Mapping[str, Any]
    destinations: Mapping[str, Any]

    def __init__(
        self,
        name: str,
        dataframe: Dataframe | None = None,
        event: Event | None = None,
        audit: Audit | None = None,
        processors: Mapping[str, DataProcessor] | None = None,
        sources: Mapping[str, Any] | None = None,
        destinations: Mapping[str, Any] | None = None,
        source: Source | None = None,
        destination: Destination | None = None,
        messaging: Messaging | None = None,
    ) -> None:
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "dataframe", dataframe or Dataframe())
        object.__setattr__(self, "event", event or Event())
        object.__setattr__(self, "audit", audit or Audit())
        object.__setattr__(self, "processors", dict(processors or {}))

        source_mapping = dict(sources or {})
        source_mapping.update(_source_mapping(source, messaging))
        destination_mapping = dict(destinations or {})
        destination_mapping.update(_destination_mapping(destination))

        object.__setattr__(self, "sources", source_mapping)
        object.__setattr__(self, "destinations", destination_mapping)

    @property
    def source(self) -> EndpointView:
        return EndpointView(self.sources)

    @property
    def destination(self) -> EndpointView:
        return EndpointView(self.destinations)

    def get_source(self, name: str) -> Any:
        return self.sources[name]

    def get_destination(self, name: str) -> Any:
        return self.destinations[name]

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
    def datalake(self) -> DataLakeEndpoint:
        return self.destination.datalake

    @property
    def database(self) -> DatabaseEndpoint:
        return self.destination.database

    @property
    def table_name(self) -> str:
        return self.database.table_name

    @property
    def datawarehouse(self) -> DataWarehouseEndpoint:
        return self.destination.datawarehouse

    @property
    def messaging(self) -> MessagingEndpoint:
        if "messaging" in self.sources:
            return self.source.messaging
        if "messaging" in self.destinations:
            return self.destination.messaging
        return MessagingEndpoint()

    @property
    def streaming(self) -> MessagingEndpoint:
        return self.messaging

    @property
    def streaming_topic(self) -> str:
        return self.messaging.topic

    @property
    def audit_topic(self) -> str:
        return self.audit.topic
