from data_platform.model.dataset import Dataset
from data_platform.registry.registry import Registry


class DatasetRegistry(Registry[Dataset]):
    def __init__(self) -> None:
        super().__init__("dataset", str.lower)


dataset_registry = DatasetRegistry()

