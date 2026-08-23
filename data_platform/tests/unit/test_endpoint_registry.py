import pytest

from data_platform.registry.endpoint_registry import EndpointRegistry, endpoint_registry
from data_platform.domain.house.dataset import HOUSE_DATASET
from data_platform.domain.sale.dataset import SALE_DATASET
from data_platform.registry.endpoint_registry import audit_endpoint
from data_platform.model import FileEndpoint


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
        assert endpoint_registry.get_item(audit_endpoint.name) is audit_endpoint
        assert SALE_DATASET.audit is audit_endpoint
        assert HOUSE_DATASET.audit is audit_endpoint
