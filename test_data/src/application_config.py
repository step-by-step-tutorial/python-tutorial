
from collections.abc import Sequence
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any

import env_config
from exceptions import ConfigurationError
from file_utils import read_json_file

DERIVED_TYPE = "derived"
DEFAULT_DESTINATIONS = ("csv",)
ALLOWED_DESTINATIONS = ("csv", "json", "database", "kafka")


@dataclass(frozen=True)
class ColumnConfig:

    name: str
    type: str
    file: str | None = None
    method: str | None = None
    domain: str | None = None
    value: str | None = None
    start: int | None = None
    step: int | None = None
    min: int | None = None
    max: int | None = None
    date_start: str | None = None
    date_end: str | None = None
    source_field: str | None = None
    mapping_file: str | None = None
    key_column: str | None = None
    value_column: str | None = None
    file_column: str | None = None
    file_columns: tuple[str, ...] | None = None
    separator: str | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ColumnConfig":
        label = raw.get("name", "<unnamed>")
        unknown = sorted(set(raw) - {field.name for field in fields(cls)})
        if unknown:
            raise ConfigurationError(
                f"Column {label!r} has unknown keys: {', '.join(unknown)}."
            )

        for required in ("name", "type"):
            if not raw.get(required):
                raise ConfigurationError(f"Every column needs a {required!r}: {raw!r}")

        data = dict(raw)
        file_columns = data.get("file_columns")
        if file_columns is not None:
            if not isinstance(file_columns, list) or not file_columns:
                raise ConfigurationError(
                    f"Column {label!r}: 'file_columns' must be a non-empty list."
                )
            data["file_columns"] = tuple(file_columns)

        return cls(**data)


@dataclass(frozen=True)
class GeneratorConfig:

    row_count: int
    output_file: str
    columns: Sequence[ColumnConfig]
    seed: int | None = None
    destinations: tuple[str, ...] = DEFAULT_DESTINATIONS

    @property
    def headers(self) -> tuple[str, ...]:
        return tuple(column.name for column in self.columns)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "GeneratorConfig":
        for required in ("row_count", "output_file", "columns"):
            if required not in raw:
                raise ConfigurationError(f"Config is missing the {required!r} key.")

        row_count = raw["row_count"]
        if not isinstance(row_count, int) or isinstance(row_count, bool) or row_count < 0:
            raise ConfigurationError(f"'row_count' must be a non-negative integer, got {row_count!r}.")

        raw_columns = raw["columns"]
        if not isinstance(raw_columns, list) or not raw_columns:
            raise ConfigurationError("'columns' must be a non-empty list.")

        columns = tuple(ColumnConfig.from_dict(column) for column in raw_columns)
        duplicates = sorted(
            {column.name for column in columns if [c.name for c in columns].count(column.name) > 1}
        )
        if duplicates:
            raise ConfigurationError(f"Duplicate column names: {', '.join(duplicates)}.")

        destinations = _parse_destinations(raw.get("destinations", raw.get("destination")))

        return cls(
            row_count=row_count,
            output_file=str(raw["output_file"]),
            columns=columns,
            seed=raw.get("seed"),
            destinations=destinations,
        )


def load_config(config_name: Path | str) -> GeneratorConfig:
    path = env_config.CONFIG_DIR / Path(config_name).name
    raw = read_json_file(path)
    return GeneratorConfig.from_dict(raw)


def _parse_destinations(raw: Any) -> tuple[str, ...]:
    if raw is None:
        return DEFAULT_DESTINATIONS

    if isinstance(raw, str):
        items = [raw]
    elif isinstance(raw, Sequence):
        items = list(raw)
    else:
        raise ConfigurationError(f"'destinations' must be a string or a list of strings, got {raw!r}.")

    normalized: list[str] = []
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, str):
            raise ConfigurationError(f"'destinations' must contain strings only, got {item!r}.")
        name = item.strip().lower()
        if not name:
            raise ConfigurationError("'destinations' cannot contain empty values.")
        if name not in ALLOWED_DESTINATIONS:
            allowed = ", ".join(ALLOWED_DESTINATIONS)
            raise ConfigurationError(f"Unsupported destination {name!r}. Available: {allowed}.")
        if name not in seen:
            seen.add(name)
            normalized.append(name)

    return tuple(normalized) if normalized else DEFAULT_DESTINATIONS
