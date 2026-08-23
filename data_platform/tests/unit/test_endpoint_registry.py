import pytest

from data_platform.dataset.endpoint_registry import EndpointRegistry, endpoint_registry
from data_platform.dataset.house_config import HOUSE_DATASET
from data_platform.dataset.sale_config import SALE_DATASET
from data_platform.dataset.shared_endpoints import AUDIT_ENDPOINT
from data_platform.model import FileEndpoint


class TestEndpointRegistry:
    def test_should_return_registered_endpoint(self) -> None:
        registry = EndpointRegistry()
        endpoint = FileEndpoint(name="example.file")
        registry.register(endpoint)

        assert registry.get("example.file") is endpoint

    def test_should_reject_duplicate_or_unknown_endpoint(self) -> None:
        registry = EndpointRegistry()
        registry.register(FileEndpoint(name="example.file"))

        with pytest.raises(ValueError, match="already registered"):
            registry.register(FileEndpoint(name="example.file"))

        with pytest.raises(ValueError, match="Unsupported endpoint"):
            registry.get("missing")

    def test_should_share_audit_endpoint_between_datasets(self) -> None:
        assert endpoint_registry.get(AUDIT_ENDPOINT.name) is AUDIT_ENDPOINT
        assert SALE_DATASET.audit is AUDIT_ENDPOINT
        assert HOUSE_DATASET.audit is AUDIT_ENDPOINT
