from __future__ import annotations

import env_config
from config_utils import read_config
from file_utils import list_of_file_names
from schemas import Dataset, DatasetMetadata


class DatasetRegistry:
    def __init__(self) -> None:
        self._datasets = {
            name: Dataset(name=name, config=read_config(name)) for name in list_of_file_names(env_config.CONFIG_DIR)
        }

    def get_all_datasets(self) -> list[Dataset]:
        return list(self._datasets.values())

    def get_all_names(self) -> list[str]:
        return list(self._datasets)

    def get_one(self, name: str) -> Dataset:
        dataset = self._datasets.get(name)
        if dataset is None:
            raise Exception(f"Dataset {name} not found.")
        return dataset

    def get_all_metadata(self) -> list[DatasetMetadata]:
        return [dataset.get_metadata() for dataset in self.get_all_datasets()]
