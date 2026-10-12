from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import cast

from data_platform.model.dataframe_model import DataFrameModel
from data_platform.model.endpoint_model import AuditEndpointModel, EndpointModel, EndpointType
from data_platform.model.pipeline_flow_model import PipelineFlowModel


@dataclass(frozen=True)
class DatasetModel:
    name: str
    audit: AuditEndpointModel
    dataframe: DataFrameModel = field(default_factory=DataFrameModel)
    endpoints: Mapping[str, EndpointModel] = field(default_factory=dict)
    flow: PipelineFlowModel = field(default_factory=PipelineFlowModel)

    def get_endpoint(self, name: str, endpoint_type: type[EndpointType]) -> EndpointType:
        endpoint = self.endpoints[name]
        if not isinstance(endpoint, endpoint_type):
            raise TypeError(f"Endpoint '{name}' is not a {endpoint_type.__name__}")
        return cast(EndpointType, endpoint)
