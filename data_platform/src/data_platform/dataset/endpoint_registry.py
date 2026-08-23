from data_platform.model import Endpoint


class EndpointRegistry:
    def __init__(self) -> None:
        self._endpoints: dict[str, Endpoint] = {}

    def register(self, endpoint: Endpoint) -> None:
        if endpoint.name in self._endpoints:
            raise ValueError(f"Endpoint is already registered: {endpoint.name}")
        self._endpoints[endpoint.name] = endpoint

    def get(self, name: str) -> Endpoint:
        try:
            return self._endpoints[name]
        except KeyError as error:
            raise ValueError(f"Unsupported endpoint: {name}") from error


endpoint_registry = EndpointRegistry()
