from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import env_config
from output_format_utils import output_file_name
from pydantic import BaseModel, Field


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
    key_column: str | None = None
    value_column: str | None = None
    file_column: str | None = None
    file_columns: tuple[str, ...] | None = None
    separator: str | None = None


@dataclass(frozen=True)
class ConfigModel:
    name: str
    row_count: int
    output_file: str
    columns: Sequence[ColumnModel]
    destinations: tuple[str, ...]
    column_names: tuple[str, ...]


@dataclass(frozen=True)
class Dataset:
    name: str
    config: ConfigModel

    @property
    def columns(self) -> tuple[str, ...]:
        return self.config.column_names

    @property
    def destinations(self) -> tuple[str, ...]:
        return self.config.destinations

    @property
    def output_file(self) -> Path:
        return self.output_file_for("csv")

    def output_file_for(self, format_name: str) -> Path:
        return env_config.OUTPUT_DIR / output_file_name(self.config.output_file, format_name)

    def get_metadata(self) -> "DatasetMetadata":
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


class DatasetMetadata(BaseModel):
    name: str
    config_file: str
    row_count: int
    column_count: int
    columns: list[str]
    destinations: list[str]
    file: str = Field(description="Path relative to the project root")
    download_url: str


class DatabasePage(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[dict[str, str | None]]
