from dataclasses import dataclass
from pathlib import Path

from test_data.model.config_model import ConfigModel


@dataclass(frozen=True)
class DatasetModel:
    name: str
    config: ConfigModel

    @classmethod
    def from_config(cls, config: ConfigModel) -> "DatasetModel":
        return cls(name=config.dataset_name, config=config)

    @property
    def columns(self) -> tuple[str, ...]:
        return self.config.column_names

    @property
    def destinations(self) -> tuple[str, ...]:
        return self.config.destinations

    @property
    def output_file(self) -> Path:
        return self.config.output_file("csv")
