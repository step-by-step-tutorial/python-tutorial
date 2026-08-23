from data_platform.model import Dataset
from data_platform.registry.base_registry import Registry


class DatasetRegistry(Registry[Dataset]):
    def __init__(self) -> None:
        super().__init__("dataset", str.lower)


dataset_registry = DatasetRegistry()
