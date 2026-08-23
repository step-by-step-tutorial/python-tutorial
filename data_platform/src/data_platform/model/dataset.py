from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, cast
from data_platform.model.data_processor import DataProcessor
from data_platform.model.data_frame_definition import DataFrameDefinition
from data_platform.model.endpoints import AuditEndpoint, Endpoint, EndpointType


@dataclass(frozen=True)
class Dataset:
    name: str
    audit: AuditEndpoint
    dataframe: DataFrameDefinition = field(default_factory=DataFrameDefinition)
    processors: Mapping[str, DataProcessor] = field(default_factory=dict)
    endpoints: Mapping[str, Endpoint] = field(default_factory=dict)

    def get_endpoint(self, name: str, endpoint_type: type[EndpointType]) -> EndpointType:
        endpoint = self.endpoints[name]
        if not isinstance(endpoint, endpoint_type):
            raise TypeError(f"Endpoint '{name}' is not a {endpoint_type.__name__}")
        return cast(EndpointType, endpoint)

    def get_processor(self, name: str) -> DataProcessor:
        return self.processors[name]

    @property
    def dataframe_schema(self) -> Any:
        return self.dataframe.schema

    @property
    def required_columns(self) -> frozenset[str]:
        return self.dataframe.required_columns
