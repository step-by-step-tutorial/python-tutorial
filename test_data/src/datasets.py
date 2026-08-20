from __future__ import annotations

from dataclasses import dataclass

import env_config
from application_config import GeneratorConfig, load_config
from file_utils import list_of_file_names, output_file_path, relative_to_project_root
from schemas import DatasetSummary

@dataclass(frozen=True)
class Dataset:
    name: str
    config: GeneratorConfig

    @property
    def columns(self) -> tuple[str, ...]:
        return self.config.headers

    @property
    def destinations(self) -> tuple[str, ...]:
        return self.config.destinations

    def to_summary(self) -> DatasetSummary:
        output_path = output_file_path(self.config.output_file)
        return DatasetSummary(
            name=self.name,
            config_file=relative_to_project_root(env_config.CONFIG_DIR / self.name),
            row_count=self.config.row_count,
            column_count=len(self.columns),
            destinations=list(self.destinations),
            file=relative_to_project_root(output_path),
            download_url=f"/datasets/{self.name}/download",
        )


class DatasetRegistry:
    def __init__(self) -> None:
        self._datasets = {
            name: Dataset(name=name, config=load_config(name)) for name in list_of_file_names(env_config.CONFIG_DIR)
        }

    def list(self) -> list[Dataset]:
        return list(self._datasets.values())

    def get(self, name: str) -> Dataset:
        dataset = self._datasets.get(name)
        if dataset is None:
            raise Exception(f"Dataset {name} not found.")
        return dataset
