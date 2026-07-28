"""Dataset discovery.

A dataset is a ``config_<name>.json`` file in the project root plus the CSV it
produces. The registry finds them, reports whether each has been generated, and
reads rows back — the shared vocabulary the REST API is built on.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import islice
from pathlib import Path

from application_config import GeneratorConfig, load_config
from exceptions import DatasetNotFoundError, OutputNotFoundError
from generator import CsvDataGenerator, GenerationResult

CONFIG_PREFIX = "config_"
CONFIG_SUFFIX = ".json"
CONFIG_PATTERN = f"{CONFIG_PREFIX}*{CONFIG_SUFFIX}"


@dataclass(frozen=True)
class OutputStatus:
    """State of a dataset's CSV file on disk."""

    exists: bool
    path: Path
    size_bytes: int | None = None
    modified_at: datetime | None = None
    row_count: int | None = None


@dataclass(frozen=True)
class Dataset:
    """A config file and the CSV it describes."""

    name: str
    config_path: Path
    config: GeneratorConfig

    @property
    def output_path(self) -> Path:
        return self.config_path.parent / self.config.output_file

    @property
    def columns(self) -> tuple[str, ...]:
        return self.config.headers

    @property
    def configured_row_count(self) -> int:
        return self.config.row_count


class DatasetRegistry:
    """Finds, generates, and reads the datasets of one project folder."""

    def __init__(self, project_root: Path) -> None:
        self._root = Path(project_root).resolve()

    @property
    def project_root(self) -> Path:
        return self._root

    def names(self) -> list[str]:
        """Dataset names, sorted, taken from the ``config_<name>.json`` files."""
        return sorted(
            path.name[len(CONFIG_PREFIX) : -len(CONFIG_SUFFIX)]
            for path in self._root.glob(CONFIG_PATTERN)
        )

    def list(self) -> list[Dataset]:
        """Every dataset whose config file loads successfully."""
        return [self.get(name) for name in self.names()]

    def get(self, name: str) -> Dataset:
        """Look one dataset up by name.

        Raises:
            DatasetNotFoundError: no config file matches the name.
            ConfigurationError: the config file exists but is not usable.
        """
        config_path = self._root / f"{CONFIG_PREFIX}{name}{CONFIG_SUFFIX}"
        if name not in set(self.names()) or not config_path.is_file():
            known = ", ".join(self.names()) or "none"
            raise DatasetNotFoundError(f"Unknown dataset {name!r}. Available: {known}.")

        return Dataset(name=name, config_path=config_path, config=load_config(config_path))

    def status(self, dataset: Dataset) -> OutputStatus:
        """Whether the dataset's CSV exists, and its size, age, and row count."""
        path = dataset.output_path
        if not path.is_file():
            return OutputStatus(exists=False, path=path)

        stat = path.stat()
        return OutputStatus(
            exists=True,
            path=path,
            size_bytes=stat.st_size,
            modified_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
            row_count=self._count_rows(path),
        )

    def generate(self, name: str) -> GenerationResult:
        """Regenerate one dataset's CSV, replacing any existing file."""
        dataset = self.get(name)
        generator = CsvDataGenerator(
            config=dataset.config,
            project_root=dataset.config_path.parent,
        )
        return generator.generate()

    def read_rows(self, name: str, offset: int = 0, limit: int = 100) -> list[dict[str, str]]:
        """Read a page of rows back from a generated CSV.

        Raises:
            OutputNotFoundError: the dataset has not been generated yet.
        """
        path = self.output_file(name)
        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            return [dict(row) for row in islice(reader, offset, offset + limit)]

    def output_file(self, name: str) -> Path:
        """Path of a generated CSV, checked to exist.

        Raises:
            OutputNotFoundError: the dataset has not been generated yet.
        """
        dataset = self.get(name)
        path = dataset.output_path
        if not path.is_file():
            raise OutputNotFoundError(
                f"Dataset {name!r} has not been generated yet. "
                f"POST /datasets/{name}/generate first."
            )
        return path

    @staticmethod
    def _count_rows(path: Path) -> int:
        with path.open("r", encoding="utf-8", newline="") as file:
            return max(sum(1 for _ in csv.reader(file)) - 1, 0)
