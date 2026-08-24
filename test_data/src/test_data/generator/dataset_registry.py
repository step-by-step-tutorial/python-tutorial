from __future__ import annotations

from pathlib import Path

from test_data.config import settings as env_config
from test_data.config.config_utils import read_config
from test_data.model.schemas import Dataset, DatasetMetadata
from test_data.util.file_utils import list_of_file_names


class DatasetRegistry:
    def __init__(self) -> None:
        self._datasets = {
            Path(name).stem: Dataset(name=Path(name).stem, config=read_config(name))
            for name in list_of_file_names(env_config.CONFIG_DIR)
        }

    def get_all_datasets(self) -> list[Dataset]:
        return list(self._datasets.values())

    def get_all_names(self) -> list[str]:
        return list(self._datasets)

    def get_one(self, name: str) -> Dataset:
        return self._datasets[name]

    def get_all_metadata(self) -> list[DatasetMetadata]:
        return [dataset.get_metadata() for dataset in self.get_all_datasets()]
