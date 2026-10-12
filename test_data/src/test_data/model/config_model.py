from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from test_data.config import settings as env_config
from test_data.model.column_model import ColumnModel
from test_data.util.json_utils import read_json_file


@dataclass(frozen=True)
class ConfigModel:
    name: str
    row_count: int
    output_name: str
    columns: Sequence[ColumnModel]
    destinations: tuple[str, ...]
    column_names: tuple[str, ...]
    kafka_topic: str
    kafka_key_column: str

    @classmethod
    def from_dict(cls, raw: dict[str, Any], name: str = "") -> "ConfigModel":
        columns = tuple(ColumnModel.from_dict(column) for column in raw["columns"])
        return cls(
            name=name,
            row_count=raw["row_count"],
            output_name=raw["output_name"],
            columns=columns,
            destinations=tuple(raw["destinations"]),
            column_names=tuple(column.name for column in columns),
            kafka_topic=raw["kafka_topic"],
            kafka_key_column=raw["kafka_key_column"],
        )

    @classmethod
    def from_file(cls, config: str | Path) -> "ConfigModel":
        """Load a config by name from CONFIG_DIR (".json" is optional), or from a path to a config file."""
        path = Path(config)
        if path.suffix == "":
            path = path.with_suffix(".json")
        if (env_config.CONFIG_DIR / path).is_file():
            path = env_config.CONFIG_DIR / path

        return cls.from_dict(read_json_file(path), path.name)

    @property
    def dataset_name(self) -> str:
        return Path(self.name).stem

    @property
    def table_name(self) -> str:
        return Path(self.output_name).stem

    def output_file(self, format_name: str) -> Path:
        """Path of the generated file for a file format (csv, json, xml), named after output_name."""
        return env_config.OUTPUT_DIR / Path(self.output_name).with_suffix(f".{format_name}")
