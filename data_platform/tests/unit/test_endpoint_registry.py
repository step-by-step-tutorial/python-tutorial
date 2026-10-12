import pytest

from data_platform.config.key import Key
from data_platform.config.pipeline_type import PipelineType
from data_platform.model.endpoint_model import FileEndpointModel
from data_platform.registry.bootstrap import initialize_registries
from data_platform.registry.dataset_registry import dataset_registry
from data_platform.registry.endpoint_registry import EndpointRegistry, endpoint_registry


class TestEndpointRegistry:
    def test_should_return_registered_endpoint(self) -> None:
        registry = EndpointRegistry()
        endpoint = FileEndpointModel(name="example.file")
        registry.register(endpoint.name, endpoint)

        assert registry.get_item("example.file") is endpoint

    def test_should_reject_duplicate_or_unknown_endpoint(self) -> None:
        registry = EndpointRegistry()
        endpoint = FileEndpointModel(name="example.file")
        registry.register(endpoint.name, endpoint)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(endpoint.name, endpoint)

        with pytest.raises(ValueError, match="Unsupported endpoint"):
            registry.get_item("missing")

    def test_should_share_audit_endpoint_between_datasets(self) -> None:
        initialize_registries()
        audit_endpoint = endpoint_registry.get_item(Key.AUDIT)

        house = dataset_registry.create_dataset("house", PipelineType.INMEMORY)
        online_shopping = dataset_registry.create_dataset("online_shopping", PipelineType.INMEMORY)

        assert house.audit is audit_endpoint
        assert online_shopping.audit is audit_endpoint
