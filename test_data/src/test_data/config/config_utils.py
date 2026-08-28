from typing import Any
from pathlib import Path

from test_data.config import settings as env_config
from test_data.model.schemas import ColumnModel, ConfigModel
from test_data.util.json_utils import read_json_file


def convert_to_column(raw_column: dict[str, Any]) -> ColumnModel:
    data = dict(raw_column)
    if data.get("source_fields") is not None:
        data["source_fields"] = tuple(data["source_fields"])
    if data.get("file_columns") is not None:
        data["file_columns"] = tuple(data["file_columns"])
    if data.get("filter_values") is not None:
        data["filter_values"] = tuple(data["filter_values"])
    if data.get("filter_fallback_values") is not None:
        data["filter_fallback_values"] = tuple(data["filter_fallback_values"])
    if data.get("required_columns") is not None:
        data["required_columns"] = tuple(data["required_columns"])
    if data.get("exclude_directories") is not None:
        data["exclude_directories"] = tuple(data["exclude_directories"])

    return ColumnModel(**data)


def convert_to_columns(raw_columns: list[dict[str, Any]]) -> tuple[ColumnModel, ...]:
    return tuple(convert_to_column(column) for column in raw_columns)


def convert_to_config(raw_config: dict[str, Any], name: str = "") -> ConfigModel:
    columns = convert_to_columns(raw_config["columns"])
    return ConfigModel(
        name=name,
        row_count=raw_config["row_count"],
        output_name=raw_config["output_name"],
        columns=columns,
        destinations=tuple(raw_config["destinations"]),
        column_names=tuple(column.name for column in columns),
        kafka_topic=raw_config["kafka_topic"],
        kafka_key_column=raw_config["kafka_key_column"],
    )


def read_config(file_name: str) -> ConfigModel:
    config_name = Path(file_name)
    if config_name.suffix == "":
        config_name = config_name.with_suffix(".json")

    return convert_to_config(read_json_file(env_config.CONFIG_DIR / config_name), config_name.name)
