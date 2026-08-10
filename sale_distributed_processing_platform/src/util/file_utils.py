import csv
from collections.abc import Callable
from pathlib import Path
from typing import Any

from app_config import env_config as ec
from util.string_utils import should_be_not_none

ROOT = Path(__file__).resolve().parents[2]


def should_be_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"File {path} does not exist")


def absolute_path(path: Path) -> Path:
    full_path = ROOT / path
    should_be_exists(full_path)
    return full_path


def read_sql_file(file_name: str) -> str:
    return (absolute_path(ec.SCRIPTS_DIR) / file_name).read_text(encoding="utf-8")


def read_csv_file(path: Path, processor: Callable[[dict[str, Any]], None]) -> int:
    should_be_not_none(path, "CSV file path")
    should_be_not_none(processor, "CSV row processor")
    should_be_exists(path)

    row_counter = 0

    with path.open(mode="r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            processor(row)
            row_counter += 1

    return row_counter
