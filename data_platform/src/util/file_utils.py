import csv
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from config.app import settings as app_settings
from util.string_utils import should_not_be_none

logger = logging.getLogger(__name__)


def should_be_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"File {path} does not exist")


def generate_full_file_path(path: Path) -> Path:
    full_path = app_settings.root / path
    should_be_exists(full_path)
    return full_path


def read_text_file(file_name: str) -> str:
    path = generate_full_file_path(app_settings.scripts_dir) / file_name
    logger.info("Reading SQL file from %s", path)
    return path.read_text(encoding="utf-8")


def read_csv_file(path_str: str, consumer: Callable[[dict[str, Any]], None]) -> int:
    should_not_be_none(path_str, "CSV file path")
    should_not_be_none(consumer, "CSV row processor")
    path = Path(path_str)
    should_be_exists(path)
    logger.info("Reading CSV file from %s", path_str)

    row_counter = 0

    with path.open(mode="r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            consumer(row)
            row_counter += 1

    return row_counter
