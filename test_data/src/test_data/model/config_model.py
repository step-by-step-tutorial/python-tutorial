from dataclasses import dataclass
from pathlib import Path
from typing import Any

from test_data.model.column_model import ColumnModel
from test_data.model.settings_model import SettingsModel
from test_data.util.json_utils import read_json_file


@dataclass(frozen=True)
class ConfigModel:
    """One dataset: its JSON config plus the directory its output files are written to."""
    name: str
    row_count: int
    output_name: str
    columns: tuple[ColumnModel, ...]
    destinations: tuple[str, ...]
    kafka_topic: str
    kafka_key_column: str
    output_dir: Path

    @classmethod
    def from_dict(cls, raw: dict[str, Any], name: str, output_dir: Path) -> "ConfigModel":
        return cls(
            name=name,
            row_count=raw["row_count"],
            output_name=raw["output_name"],
            columns=tuple(ColumnModel.from_dict(column) for column in raw["columns"]),
            destinations=tuple(raw["destinations"]),
            kafka_topic=raw["kafka_topic"],
            kafka_key_column=raw["kafka_key_column"],
            output_dir=output_dir,
        )

    @classmethod
    def from_file(cls, config: str | Path, settings: SettingsModel) -> "ConfigModel":
        """Load a config by name from the config directory (".json" is optional), or from a path to a config file."""
        path = Path(config)
        if path.suffix == "":
            path = path.with_suffix(".json")
        if (settings.config_dir / path).is_file():
            path = settings.config_dir / path

        return cls.from_dict(read_json_file(path), path.name, settings.output_dir)

    @property
    def column_names(self) -> tuple[str, ...]:
        return tuple(column.name for column in self.columns)

    @property
    def dataset_name(self) -> str:
        return Path(self.name).stem

    @property
    def table_name(self) -> str:
        return Path(self.output_name).stem

    def output_file(self, format_name: str) -> Path:
        """Path of the generated file for a file format (csv, json, xml), named after output_name."""
        return self.output_dir / Path(self.output_name).with_suffix(f".{format_name}")
