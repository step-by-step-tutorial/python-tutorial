from typing import Any

import env_config
from json_utils import read_json_file
from schemas import ColumnModel, ConfigModel


def convert_to_column(raw_column: dict[str, Any]) -> ColumnModel:
    data = dict(raw_column)
    if data.get("source_fields") is not None:
        data["source_fields"] = tuple(data["source_fields"])
    if data.get("file_columns") is not None:
        data["file_columns"] = tuple(data["file_columns"])

    return ColumnModel(**data)


def convert_to_columns(raw_columns: list[dict[str, Any]]) -> tuple[ColumnModel, ...]:
    return tuple(convert_to_column(column) for column in raw_columns)


def convert_to_config(raw_config: dict[str, Any], name: str = "") -> ConfigModel:
    columns = convert_to_columns(raw_config["columns"])
    return ConfigModel(
        name=name,
        row_count=raw_config["row_count"],
        output_file=str(raw_config["output_file"]),
        columns=columns,
        destinations=tuple(raw_config["destinations"]),
        column_names=tuple(column.name for column in columns),
    )


def read_config(file_name: str) -> ConfigModel:
    return convert_to_config(read_json_file(env_config.CONFIG_DIR / file_name), file_name)
