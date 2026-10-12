from data_platform.audit.audit_registration import register_audit
from data_platform.domain.house.house_registration import register_house
from data_platform.domain.online_shopping.online_shopping_registration import register_online_shopping
from data_platform.registry.connection_registry import connection_registry
from data_platform.registry.dataset_registry import dataset_registry
from data_platform.registry.endpoint_registry import endpoint_registry


def initialize_registries() -> None:
    connection_registry.clear()
    endpoint_registry.clear()
    dataset_registry.clear()

    register_audit()
    register_house()
    register_online_shopping()
