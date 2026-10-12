from collections.abc import Callable

from data_platform.config.pipeline_type import PipelineType
from data_platform.model.dataset_model import DatasetModel
from data_platform.registry.registry import Registry

DatasetFactory = Callable[[PipelineType], DatasetModel]


class DatasetRegistry(Registry[DatasetFactory]):
    def __init__(self) -> None:
        super().__init__("dataset", str.lower)

    def create_dataset(self, name: str, pipeline_type: PipelineType) -> DatasetModel:
        return self.get_item(name)(pipeline_type)


dataset_registry = DatasetRegistry()
