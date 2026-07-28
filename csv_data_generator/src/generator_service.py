from __future__ import annotations

import csv
import json
import random
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ColumnConfig:
    name: str
    type: str
    file: str | None = None
    method: str | None = None
    domain: str | None = None
    value: str | None = None


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

    def generate_rows(self) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for _ in range(self.config.row_count):
            row: dict[str, str] = {}
            for column in self.config.columns:
                row[column.name] = self._generate_value(column, row)
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

    def _generate_value(self, column: ColumnConfig, row: dict[str, str]) -> str:
        if column.type == "random_from_file":
            return self._random_from_file(column)
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

        raise ValueError(f"Unsupported derived method: {column.method}")
