from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import env_config
from config_utils import read_config
from file_utils import list_of_file_names
from schemas import ConfigModel
from schemas import DatasetMetadata

@dataclass(frozen=True)
class Dataset:
    name: str
    config: ConfigModel

    @property
    def columns(self) -> tuple[str, ...]:
        return self.config.headers

    @property
    def destinations(self) -> tuple[str, ...]:
        return self.config.destinations

    @property
    def output_file(self) -> Path:
        return env_config.OUTPUT_DIR / self.config.output_file

    def get_metadata(self) -> DatasetMetadata:
        return DatasetMetadata(
            name=self.name,
            config_file=f"{env_config.CONFIG_DIR.name}/{self.name}",
            row_count=self.config.row_count,
            column_count=len(self.columns),
            columns=list(self.columns),
            destinations=list(self.destinations),
            file=f"{env_config.OUTPUT_DIR.name}/{self.config.output_file}",
            download_url=f"/datasets/{self.name}/download",
        )


class DatasetRegistry:
    def __init__(self) -> None:
        self._datasets = {
            name: Dataset(name=name, config=read_config(name)) for name in list_of_file_names(env_config.CONFIG_DIR)
        }

    def get_all_datasets(self) -> get_all_datasets[Dataset]:
        return list(self._datasets.values())

    def get_one(self, name: str) -> Dataset:
        dataset = self._datasets.get(name)
        if dataset is None:
            raise Exception(f"Dataset {name} not found.")
        return dataset

    def get_all_metadata(self) -> list[DatasetMetadata]:
        return [dataset.get_metadata() for dataset in self.get_all_datasets()]
