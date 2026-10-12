from data_platform.model.endpoint_model import EndpointModel
from data_platform.registry.registry import Registry


class EndpointRegistry(Registry[EndpointModel]):
    def __init__(self) -> None:
        super().__init__("endpoint")


endpoint_registry = EndpointRegistry()
