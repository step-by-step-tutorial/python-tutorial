from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol, TypeVar, cast

from config.audit import AuditSettings
from processor.base import DataProcessor


@dataclass(frozen=True)
class Dataframe:
    schema: Any = None
    required_columns: frozenset[str] = frozenset()


class Endpoint(Protocol):
    @property
    def name(self) -> str:
        ...


EndpointType = TypeVar("EndpointType", bound=Endpoint)


@dataclass(frozen=True)
class FileEndpoint:
    name: str = "file"
    file_name: str = ""
    file_path: str = ""
    file_format: str = "csv"
    encoding: str = "utf-8"


@dataclass(frozen=True)
class DatabaseEndpoint:
    name: str = "database"
    connection_name: str = ""
    schema: str = ""
    stage_table_name: str = ""
    full_stage_table_name: str = ""
    table_names: list[str] = field(default_factory=list)
    create_sql_files: Mapping[str, str] = field(default_factory=dict)
    truncate_sql_files: Mapping[str, str] = field(default_factory=dict)
    write_sql_files: Mapping[str, str] = field(default_factory=dict)
    query_sql_files: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class DataWarehouseEndpoint:
    name: str = "datawarehouse"
    connection_name: str = ""
    schema: str = ""
    table_name: str = ""
    full_table_name: str = ""
    create_sql_files: Mapping[str, str] = field(default_factory=dict)
    truncate_sql_files: Mapping[str, str] = field(default_factory=dict)
    write_sql_files: Mapping[str, str] = field(default_factory=dict)
    query_sql_files: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class DataLakeEndpoint:
    name: str = "datalake"
    connection_name: str = ""
    bucket_name: str = ""
    scheme: str = "s3a"


@dataclass(frozen=True)
class RestApiEndpoint:
    name: str = "rest_api"
    connection_name: str = ""
    url: str = ""
    method: str = "GET"
    headers: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class MessagingEndpoint:
    name: str = "messaging"
    connection_name: str = ""
    channel_name: str = ""
    bootstrap_servers: str = ""
    starting_offsets: str = "earliest"
    group_id: str = "data-platform-messaging"
    timeout_ms: int = 1000
    max_messages: int = 1000
    consumer_config: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class AuditEndpoint:
    database_connection_name: str
    messaging_connection_name: str
    datalake_connection_name: str
    create_sql_files: Mapping[str, str] = field(default_factory=dict)
    truncate_sql_files: Mapping[str, str] = field(default_factory=dict)
    write_sql_files: Mapping[str, str] = field(default_factory=dict)
    query_sql_files: Mapping[str, str] = field(default_factory=dict)
    channel_name: str = ""
    bucket_name: str = ""
    name: str = field(default="audit", init=False)


@dataclass(frozen=True)
class Dataset:
    name: str
    dataframe: Dataframe = field(default_factory=Dataframe)
    processors: Mapping[str, DataProcessor] = field(default_factory=dict)
    endpoints: Mapping[str, Endpoint] = field(default_factory=dict)
    audit: AuditEndpoint = field(
        default_factory=lambda: AuditEndpoint(
            database_connection_name="audit.database",
            messaging_connection_name="audit.kafka.producer",
            datalake_connection_name="audit.datalake",
            create_sql_files={"create": "database/audit/create_tables.sql"},
            write_sql_files={"write": "database/audit/insert_event.sql"},
        )
    )

    def get_endpoint(self, name: str, endpoint_type: type[EndpointType]) -> EndpointType:
        return cast(EndpointType, self.endpoints[name])

    def get_processor(self, name: str) -> DataProcessor:
        return self.processors[name]

    @property
    def dataframe_schema(self) -> Any:
        return self.dataframe.schema

    @property
    def required_columns(self) -> frozenset[str]:
        return self.dataframe.required_columns
