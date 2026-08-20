from __future__ import annotations

import csv
from dataclasses import dataclass
from itertools import islice
from pathlib import Path

from application_config import GeneratorConfig, load_config
from exceptions import DatasetNotFoundError, OutputNotFoundError
from generator import GenerationResult, generate_dataset
import env_config
from csv_utils import count_rows
from file_utils import list_of_file_names


@dataclass(frozen=True)
class OutputStatus:
    exists: bool
    path: Path
    row_count: int | None = None


@dataclass(frozen=True)
class Dataset:
    name: str
    config: GeneratorConfig

    @property
    def columns(self) -> tuple[str, ...]:
        return self.config.headers

    @property
    def row_count(self) -> int:
        return self.config.row_count

    @property
    def destinations(self) -> tuple[str, ...]:
        return self.config.destinations


class DatasetRegistry:
    def __init__(self) -> None:
        self._datasets = {
            name: Dataset(name=name, config=load_config(name)) for name in list_of_file_names(env_config.CONFIG_DIR)
        }

    def list(self) -> list[Dataset]:
        return list(self._datasets.values())

    def get(self, name: str) -> Dataset:
        dataset = self._datasets.get(name)
        if dataset is None:
            raise Exception(f"Dataset {name} not found.")
        return dataset

    def status(self, dataset: Dataset) -> OutputStatus:
        path = env_config.OUTPUT_DIR / dataset.config.output_file
        if not path.is_file():
            return OutputStatus(exists=False, path=path)

        return OutputStatus(
            exists=True,
            path=path,
            row_count=count_rows(path),
        )

    def generate(self, name: str) -> GenerationResult:
        self.get(name)
        return generate_dataset(name)

    def read_rows(self, name: str, offset: int = 0, limit: int = 100) -> list[dict[str, str]]:
        path = self.output_file(name)
        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            return [dict(row) for row in islice(reader, offset, offset + limit)]

    def output_file(self, name: str) -> Path:
        dataset = self.get(name)
        path = env_config.OUTPUT_DIR / dataset.config.output_file
        if not path.is_file():
            raise OutputNotFoundError(
                f"Dataset {name!r} has not been generated yet. "
                f"POST /datasets/{name}/generate first."
            )
        return path
