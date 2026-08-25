from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, cast

from data_platform.model.dataframe_model import DataFrameModel
from data_platform.model.endpoints import AuditEndpoint, Endpoint, EndpointType
from data_platform.model.pipeline_flow import PipelineFlow


@dataclass(frozen=True)
class Dataset:
    name: str
    audit: AuditEndpoint
    dataframe: DataFrameModel = field(default_factory=DataFrameModel)
    endpoints: Mapping[str, Endpoint] = field(default_factory=dict)
    flow: PipelineFlow = field(default_factory=PipelineFlow)

    def get_endpoint(self, name: str, endpoint_type: type[EndpointType]) -> EndpointType:
        endpoint = self.endpoints[name]
        if not isinstance(endpoint, endpoint_type):
            raise TypeError(f"Endpoint '{name}' is not a {endpoint_type.__name__}")
        return cast(EndpointType, endpoint)

    @property
    def dataframe_schema(self) -> Any:
        return self.dataframe.schema

    @property
    def required_columns(self) -> frozenset[str]:
        return self.dataframe.required_columns

