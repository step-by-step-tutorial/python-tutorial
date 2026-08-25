from data_platform.model.endpoints import Endpoint
from data_platform.registry.base_registry import Registry


class EndpointRegistry(Registry[Endpoint]):
    def __init__(self) -> None:
        super().__init__("endpoint")


endpoint_registry = EndpointRegistry()
