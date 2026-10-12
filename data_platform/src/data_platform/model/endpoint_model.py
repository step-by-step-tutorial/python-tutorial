from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass, field
from typing import Protocol, TypeVar

from data_platform.util.path_utils import generate_full_path


class EndpointModel(Protocol):
    @property
    def name(self) -> str:
        ...


EndpointType = TypeVar("EndpointType", bound=EndpointModel)


def _qualified_name(schema: str, name: str) -> str:
    return f"{schema}.{name}" if schema else name


@dataclass(frozen=True)
class FileEndpointModel:
    name: str = "file"
    file_name: str = ""
    file_path: str = ""
    file_format: str = "csv"
    encoding: str = "utf-8"


@dataclass(frozen=True)
class DatabaseEndpointModel:
    name: str = "database"
    connection_name: str = ""
    schema: str = ""
    stage_table_name: str = ""
    create_sql_files: Mapping[str, str] = field(default_factory=dict)
    truncate_sql_files: Mapping[str, str] = field(default_factory=dict)
    write_sql_files: Mapping[str, str] = field(default_factory=dict)
    query_sql_files: Mapping[str, str] = field(default_factory=dict)

    @property
    def full_stage_table_name(self) -> str:
        return _qualified_name(self.schema, self.stage_table_name)


@dataclass(frozen=True)
class WarehouseEndpointModel:
    name: str = "warehouse"
    connection_name: str = ""
    schema: str = ""
    table_name: str = ""
    create_sql_files: Mapping[str, str] = field(default_factory=dict)
    truncate_sql_files: Mapping[str, str] = field(default_factory=dict)
    write_sql_files: Mapping[str, str] = field(default_factory=dict)
    query_sql_files: Mapping[str, str] = field(default_factory=dict)

    @property
    def full_table_name(self) -> str:
        return _qualified_name(self.schema, self.table_name)


@dataclass(frozen=True)
class DataLakeEndpointModel:
    name: str = "datalake"
    connection_name: str = ""
    bucket_name: str = ""
    scheme: str = "s3a"

    def full_path(self, relative_path: str) -> str:
        return generate_full_path(self.bucket_name, relative_path, self.scheme)


@dataclass(frozen=True)
class RestApiEndpointModel:
    name: str = "rest_api"
    url: str = ""
    method: str = "GET"
    headers: MutableMapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class MessagingEndpointModel:
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
class AuditEndpointModel:
    database_connection_name: str
    messaging_connection_name: str
    datalake_connection_name: str
    schema: str = ""
    create_sql_files: Mapping[str, str] = field(default_factory=dict)
    truncate_sql_files: Mapping[str, str] = field(default_factory=dict)
    write_sql_files: Mapping[str, str] = field(default_factory=dict)
    query_sql_files: Mapping[str, str] = field(default_factory=dict)
    channel_name: str = ""
    bootstrap_servers: str = ""
    bucket_name: str = ""
    name: str = field(default="audit", init=False)
