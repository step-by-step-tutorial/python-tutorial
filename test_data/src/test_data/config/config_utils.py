from typing import Any

from test_data.config import settings as env_config
from test_data.model.schemas import ColumnModel, ConfigModel
from test_data.util.json_utils import read_json_file


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
        output_name=raw_config["output_name"],
        columns=columns,
        destinations=tuple(raw_config["destinations"]),
        column_names=tuple(column.name for column in columns),
        kafka_topic=raw_config["kafka_topic"],
        kafka_key_column=raw_config["kafka_key_column"],
    )


def read_config(file_name: str) -> ConfigModel:
    return convert_to_config(read_json_file(env_config.CONFIG_DIR / file_name), file_name)
