from __future__ import annotations

import csv
import json
import random
import re
import unicodedata
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


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


@dataclass(frozen=True)
class GeneratorConfig:
    row_count: int
    output_file: str
    columns: list[ColumnConfig]
    seed: int | None = None


def load_config(config_path: Path) -> GeneratorConfig:
    with config_path.open("r", encoding="utf-8") as file:
        raw_config = json.load(file)

    columns = [ColumnConfig(**column) for column in raw_config["columns"]]
    return GeneratorConfig(
        row_count=raw_config["row_count"],
        output_file=raw_config["output_file"],
        columns=columns,
        seed=raw_config.get("seed"),
    )


def load_values(file_path: Path) -> list[str]:
    with file_path.open("r", encoding="utf-8") as file:
        values = [line.strip() for line in file if line.strip()]

    if not values:
        raise ValueError(f"Source file is empty: {file_path}")

    return values


def normalize_for_email(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_value.lower().strip()
    cleaned = re.sub(r"[^a-z0-9]+", ".", lowered)
    cleaned = re.sub(r"\.+", ".", cleaned).strip(".")

    if not cleaned:
        raise ValueError("Cannot build email from empty normalized value.")

    return cleaned


class CsvDataGenerator:
    def __init__(self, config: GeneratorConfig, project_root: Path) -> None:
        self.config = config
        self.project_root = project_root
        self.random = random.Random(config.seed)
        self.file_cache: dict[str, list[str]] = {}
        self.mapping_cache: dict[str, dict[str, str]] = {}

    def generate_rows(self) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for row_index in range(self.config.row_count):
            row: dict[str, str] = {}
            for column in self.config.columns:
                row[column.name] = self._generate_value(column, row, row_index)
            rows.append(row)
        return rows

    def write_csv(self, rows: list[dict[str, str]]) -> Path:
        output_path = self.project_root / self.config.output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)

        headers = [column.name for column in self.config.columns]
        with output_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

        return output_path

    def _generate_value(
        self,
        column: ColumnConfig,
        row: dict[str, str],
        row_index: int,
    ) -> str:
        if column.type == "random_from_file":
            return self._random_from_file(column)
        if column.type == "random_from_mapped_file":
            return self._random_from_mapped_file(column, row)
        if column.type == "sequence":
            return self._sequence_value(column, row_index)
        if column.type == "random_int":
            return self._random_int_value(column)
        if column.type == "random_date":
            return self._random_date_value(column)
        if column.type == "derived":
            return self._derived_value(column, row)
        if column.type == "fixed":
            if column.value is None:
                raise ValueError(f"Missing fixed value for column: {column.name}")
            return column.value

        raise ValueError(f"Unsupported column type: {column.type}")

    def _random_from_file(self, column: ColumnConfig) -> str:
        if column.file is None:
            raise ValueError(f"Missing file for column: {column.name}")

        if column.file not in self.file_cache:
            self.file_cache[column.file] = load_values(self.project_root / column.file)

        return self.random.choice(self.file_cache[column.file])

    def _random_from_mapped_file(
        self,
        column: ColumnConfig,
        row: dict[str, str],
    ) -> str:
        if (
            column.source_field is None
            or column.mapping_file is None
            or column.key_column is None
            or column.file_column is None
        ):
            raise ValueError(
                f"random_from_mapped_file requires source_field, mapping_file, key_column, and file_column: {column.name}"
            )

        source_value = row.get(column.source_field)
        if source_value is None:
            raise ValueError(
                f"Column '{column.name}' depends on source field '{column.source_field}'."
            )

        mapping = self._get_mapping(
            mapping_file=column.mapping_file,
            key_column=column.key_column,
            value_column=column.file_column,
        )
        file_path = mapping.get(source_value)
        if file_path is None:
            raise ValueError(
                f"Value '{source_value}' not found in mapping for column '{column.name}'."
            )

        temp_column = ColumnConfig(name=column.name, type="random_from_file", file=file_path)
        return self._random_from_file(temp_column)

    def _sequence_value(self, column: ColumnConfig, row_index: int) -> str:
        start = column.start if column.start is not None else 1
        step = column.step if column.step is not None else 1
        return str(start + (row_index * step))

    def _random_int_value(self, column: ColumnConfig) -> str:
        if column.min is None or column.max is None:
            raise ValueError(
                f"Columns of type random_int require min and max: {column.name}"
            )
        return str(self.random.randint(column.min, column.max))

    def _random_date_value(self, column: ColumnConfig) -> str:
        if column.date_start is None or column.date_end is None:
            raise ValueError(
                f"Columns of type random_date require date_start and date_end: {column.name}"
            )

        start_date = date.fromisoformat(column.date_start)
        end_date = date.fromisoformat(column.date_end)
        if start_date > end_date:
            raise ValueError(
                f"date_start must be earlier than or equal to date_end: {column.name}"
            )

        day_offset = self.random.randint(0, (end_date - start_date).days)
        return (start_date + timedelta(days=day_offset)).isoformat()

    def _derived_value(self, column: ColumnConfig, row: dict[str, str]) -> str:
        if column.method == "email_from_name":
            first_name = row.get("first_name")
            last_name = row.get("last_name")
            if not first_name or not last_name:
                raise ValueError(
                    f"Column '{column.name}' depends on first_name and last_name."
                )
            domain = column.domain or "example.com"
            email_name = (
                f"{normalize_for_email(first_name)}.{normalize_for_email(last_name)}"
            )
            return f"{email_name}@{domain}"
        if column.method == "lookup_from_csv":
            return self._lookup_from_csv(column, row)

        raise ValueError(f"Unsupported derived method: {column.method}")

    def _lookup_from_csv(self, column: ColumnConfig, row: dict[str, str]) -> str:
        if (
            column.source_field is None
            or column.mapping_file is None
            or column.key_column is None
            or column.value_column is None
        ):
            raise ValueError(
                f"lookup_from_csv requires source_field, mapping_file, key_column, and value_column: {column.name}"
            )

        source_value = row.get(column.source_field)
        if source_value is None:
            raise ValueError(
                f"Column '{column.name}' depends on source field '{column.source_field}'."
            )

        mapping = self._get_mapping(
            mapping_file=column.mapping_file,
            key_column=column.key_column,
            value_column=column.value_column,
        )
        if source_value not in mapping:
            raise ValueError(
                f"Value '{source_value}' not found in mapping for column '{column.name}'."
            )

        return mapping[source_value]

    def _get_mapping(
        self,
        mapping_file: str,
        key_column: str,
        value_column: str,
    ) -> dict[str, str]:
        cache_key = f"{mapping_file}|{key_column}|{value_column}"
        if cache_key not in self.mapping_cache:
            self.mapping_cache[cache_key] = self._load_mapping(
                self.project_root / mapping_file,
                key_column,
                value_column,
            )
        return self.mapping_cache[cache_key]

    @staticmethod
    def _load_mapping(
        file_path: Path,
        key_column: str,
        value_column: str,
    ) -> dict[str, str]:
        with file_path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            mapping: dict[str, str] = {}
            for row in reader:
                key = row.get(key_column)
                value = row.get(value_column)
                if key is None or value is None:
                    raise ValueError(
                        f"Mapping file '{file_path}' must contain columns '{key_column}' and '{value_column}'."
                    )
                mapping[key] = value

        if not mapping:
            raise ValueError(f"Mapping file is empty: {file_path}")

        return mapping
