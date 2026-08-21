from collections.abc import Sequence
from dataclasses import dataclass

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
    row_count: int
    output_file: str
    columns: Sequence[ColumnModel]
    destinations: tuple[str, ...]
    headers: tuple[str, ...]


class DatasetMetadata(BaseModel):
    name: str
    config_file: str
    row_count: int
    column_count: int
    columns: list[str]
    destinations: list[str]
    file: str = Field(description="Path relative to the project root")
    download_url: str
