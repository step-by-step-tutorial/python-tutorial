from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

import env_config
from csv_utils import write_csv
from database_repository import DatabaseRepository
from json_utils import write_json

logger = logging.getLogger(__name__)


class Writer(ABC):
    name: str

    @abstractmethod
    def write(self, rows: Sequence[Mapping[str, str]], config: Any) -> None:
        raise NotImplementedError


class CsvWriter(Writer):
    name = "csv"

    def write(self, rows: Sequence[Mapping[str, str]], config: Any) -> None:
        output_path = write_csv(env_config.OUTPUT_DIR / config.output_file, config.column_names, rows)
        logger.info("CSV output written to %s", output_path)


class JsonWriter(Writer):
    name = "json"

    def write(self, rows: Sequence[Mapping[str, str]], config: Any) -> None:
        output_path = write_json(env_config.OUTPUT_DIR / f"{Path(config.output_file).stem}.json", rows)
        logger.info("JSON output written to %s", output_path)


class DatabaseWriter(Writer):
    name = "database"

    def write(self, rows: Sequence[Mapping[str, str]], config: Any) -> None:
        repository = DatabaseRepository(env_config.DATABASE_URL)
        table_name = Path(config.output_file).stem
        repository.write_rows(table_name=table_name, headers=config.column_names, rows=rows)
        logger.info("Database output written to table %s", table_name)


class WriterRegistry:
    def __init__(self) -> None:
        writers = [
            CsvWriter(),
            JsonWriter(),
            DatabaseWriter(),
        ]
        self._writers = {writer.name: writer for writer in writers}

    def write_all(self, rows: Iterable[Mapping[str, str]], config: Any) -> None:
        row_list = [dict(row) for row in rows]
        for name in config.destinations:
            self._writers[name].write(row_list, config)
