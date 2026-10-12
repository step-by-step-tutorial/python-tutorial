from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from test_data.config import settings as env_config
from test_data.util.json_utils import read_json_file


@dataclass(frozen=True)
class ColumnModel:
    name: str
    type: str
    file: str | None = None
    method: str | None = None
    formula: str | None = None
    domain: str | None = None
    value: str | None = None
    start: int | None = None
    step: int | None = None
    min: int | None = None
    max: int | None = None
    date_start: str | None = None
    date_end: str | None = None
    source_field: str | None = None
    source_fields: tuple[str, ...] | None = None
    mapping_file: str | None = None
    file_template: str | None = None
    key_column: str | None = None
    value_column: str | None = None
    value_template: str | None = None
    required_columns: tuple[str, ...] | None = None
    candidate_limit: int | None = None
    filter_column: str | None = None
    filter_values: tuple[str, ...] | None = None
    filter_fallback_values: tuple[str, ...] | None = None
    exclude_directories: tuple[str, ...] | None = None
    file_column: str | None = None
    file_columns: tuple[str, ...] | None = None
    separator: str | None = None
    nullable: bool = False
    null_probability: float | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ColumnModel":
        """Build a column from its JSON config; JSON lists become tuples so the model stays hashable."""
        data = {key: tuple(value) if isinstance(value, list) else value for key, value in raw.items()}
        return cls(**data)


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


class DatasetMetadataModel(BaseModel):
    name: str
    config_file: str
    row_count: int
    column_count: int
    columns: list[str]
    destinations: list[str]
    file: str = Field(description="Path relative to the project root")
    download_url: str

    @classmethod
    def from_dataset(cls, dataset: DatasetModel) -> "DatasetMetadataModel":
        return cls(
            name=dataset.name,
            config_file=f"{env_config.CONFIG_DIR.name}/{dataset.config.name}",
            row_count=dataset.config.row_count,
            column_count=len(dataset.columns),
            columns=list(dataset.columns),
            destinations=list(dataset.destinations),
            file=f"{env_config.OUTPUT_DIR.name}/{dataset.output_file.name}",
            download_url=f"/datasets/{dataset.name}/download",
        )


class DatabasePageModel(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[dict[str, str | None]]
