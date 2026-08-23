from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from data_platform.keys import Key
from data_platform.model.data_processor import DataProcessor
from data_platform.model.dataframe_definition import DataframeDefinition
from data_platform.model.endpoints import AuditEndpoint, Endpoint, EndpointType


@dataclass(frozen=True)
class Dataset:
    name: str
    dataframe: DataframeDefinition = field(default_factory=DataframeDefinition)
    processors: Mapping[str, DataProcessor] = field(default_factory=dict)
    endpoints: Mapping[str, Endpoint] = field(default_factory=dict)
    audit: AuditEndpoint = AuditEndpoint(
        database_connection_name=Key.AUDIT_DATABASE,
        messaging_connection_name=Key.AUDIT_KAFKA_PRODUCER,
        datalake_connection_name=Key.AUDIT_DATALAKE,
        schema="audit",
        create_sql_files={"create": "database/audit/create_tables.sql"},
        write_sql_files={"write": "database/audit/insert_event.sql"},
    )

    def get_endpoint(self, name: str, endpoint_type: type[EndpointType]) -> EndpointType:
        return self.endpoints[name]

    def get_processor(self, name: str) -> DataProcessor:
        return self.processors[name]

    @property
    def dataframe_schema(self) -> Any:
        return self.dataframe.schema

    @property
    def required_columns(self) -> frozenset[str]:
        return self.dataframe.required_columns
