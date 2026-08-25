from data_platform.registry.dataset_registry import dataset_registry
from data_platform.registry.event_converter_registry import event_converter_registry


def initialize_registries() -> None:
    from data_platform.domain.house.dataset import HOUSE_DATASET
    from data_platform.domain.house.event_converter import house_event_converter
    from data_platform.domain.sale.dataset import SALE_DATASET
    from data_platform.domain.sale.event_converter import sale_event_converter
    from data_platform.domain.online_shopping.dataset import ONLINE_SHOPPING_DATASET

    dataset_registry.clear()
    event_converter_registry.clear()
    dataset_registry.register(SALE_DATASET.pipeline_name, SALE_DATASET)
    dataset_registry.register(HOUSE_DATASET.pipeline_name, HOUSE_DATASET)
    dataset_registry.register(ONLINE_SHOPPING_DATASET.pipeline_name, ONLINE_SHOPPING_DATASET)
    event_converter_registry.register("sale", sale_event_converter)
    event_converter_registry.register("house", house_event_converter)

