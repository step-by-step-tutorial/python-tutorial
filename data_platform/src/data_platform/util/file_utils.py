import csv
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from data_platform.config.settings import settings
from data_platform.util.validation_utils import require_not_none

logger = logging.getLogger(__name__)


def require_exists(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"File {path} does not exist")
    return path


def read_text_file(file_name: str) -> str:
    path = settings.app.script_path(file_name)
    logger.info("Reading SQL file from %s", path)
    return path.read_text(encoding="utf-8")


def read_text_files(file_names: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(read_text_file(file_name) for file_name in file_names)


def read_csv_file(path_str: str, consumer: Callable[[dict[str, Any]], None]) -> int:
    require_not_none(path_str, "CSV file path")
    require_not_none(consumer, "CSV row consumer")
    path = require_exists(Path(path_str))
    logger.info("Reading CSV file from %s", path_str)

    row_counter = 0
    with path.open(mode="r", encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            consumer(row)
            row_counter += 1

    return row_counter
