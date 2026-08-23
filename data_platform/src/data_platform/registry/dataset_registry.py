from data_platform.model import Dataset
from data_platform.dataset.house_config import HOUSE_DATASET
from data_platform.dataset.sale_config import SALE_DATASET
from data_platform.registry.base_registry import Registry


class DatasetRegistry(Registry[Dataset]):
    def __init__(self) -> None:
        super().__init__("dataset", str.lower)


dataset_registry = DatasetRegistry()
dataset_registry.register(SALE_DATASET.name, SALE_DATASET)
dataset_registry.register(HOUSE_DATASET.name, HOUSE_DATASET)
