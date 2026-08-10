import logging
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.errors import EmptyDataError

logger = logging.getLogger(__name__)


def csv_to_dataframe(absolut_path: Path) -> pd.DataFrame:
    if not absolut_path.is_file():
        raise FileNotFoundError(f"CSV file not found: {absolut_path}")

    logger.info("Reading CSV file from %s", absolut_path)

    try:
        df: pd.DataFrame = pd.read_csv(absolut_path)
    except EmptyDataError as error:
        raise ValueError(f"CSV file is empty: {absolut_path}") from error
    except pd.errors.ParserError as error:
        raise ValueError(f"CSV file is invalid: {absolut_path}") from error

    if df.empty:
        raise ValueError(f"CSV file contains no data rows: {absolut_path}")

    return df


def convert_to_integer(value: str | None) -> int:
    if value is None or value.strip() == "":
        raise ValueError("Cannot convert an empty value to integer.")

    return int(value)


def convert_to_optional_float(value: str | None) -> float | None:
    if value is None or value.strip() == "":
        return None

    try:
        return float(value)
    except ValueError:
        return None


def normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None

    normalized_value = str(value).strip()

    if normalized_value == "":
        return None

    return normalized_value
