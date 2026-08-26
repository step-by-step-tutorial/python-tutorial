import pytest

from data_platform.registry.endpoint_registry import EndpointRegistry, endpoint_registry
from data_platform.registry.bootstrap import initialize_registries

initialize_registries()

from data_platform.domain.house.dataset import house_dataset
from data_platform.model.endpoints import FileEndpoint


class TestEndpointRegistry:
    def test_should_return_registered_endpoint(self) -> None:
        registry = EndpointRegistry()
        endpoint = FileEndpoint(name="example.file")
        registry.register(endpoint.name, endpoint)

        assert registry.get_item("example.file") is endpoint

    def test_should_reject_duplicate_or_unknown_endpoint(self) -> None:
        registry = EndpointRegistry()
        endpoint = FileEndpoint(name="example.file")
        registry.register(endpoint.name, endpoint)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(endpoint.name, endpoint)

        with pytest.raises(ValueError, match="Unsupported endpoint"):
            registry.get_item("missing")

    def test_should_share_audit_endpoint_between_datasets(self) -> None:
        audit_endpoint = endpoint_registry.get_item("audit")
        assert endpoint_registry.get_item("audit") is audit_endpoint
        assert house_dataset.audit == audit_endpoint
