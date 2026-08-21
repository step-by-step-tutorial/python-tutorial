from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import env_config
from json_utils import read_json_file

DERIVED_TYPE = "derived"


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
    seed: int | None = None

def convert_to_column_model(raw: dict[str, Any]) -> ColumnModel:
    data = dict(raw)
    if data.get("source_fields") is not None:
        data["source_fields"] = tuple(data["source_fields"])
    if data.get("file_columns") is not None:
        data["file_columns"] = tuple(data["file_columns"])

    return ColumnModel(**data)


def convert_to_column_model_list(raw_columns: Sequence[dict[str, Any]]) -> tuple[ColumnModel, ...]:
    return tuple(convert_to_column_model(column) for column in raw_columns)


def convert_to_config_model(raw: dict[str, Any]) -> ConfigModel:
    columns = convert_to_column_model_list(raw["columns"])
    return ConfigModel(
        row_count=raw["row_count"],
        output_file=str(raw["output_file"]),
        columns=columns,
        seed=raw.get("seed"),
        destinations=tuple(raw["destinations"]),
        headers=tuple(column.name for column in columns),
    )


def load_config(config_name: str) -> ConfigModel:
    return convert_to_config_model(read_json_file(env_config.CONFIG_DIR / config_name))
