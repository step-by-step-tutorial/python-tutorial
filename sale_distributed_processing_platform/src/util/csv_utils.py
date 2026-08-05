from pathlib import Path
from typing import Any

import pandas as pd
from pandas.errors import EmptyDataError


def read_csv_file(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")

    try:
        df: pd.DataFrame = pd.read_csv(path)
    except EmptyDataError as error:
        raise ValueError(f"CSV file is empty: {path}") from error
    except pd.errors.ParserError as error:
        raise ValueError(f"CSV file is invalid: {path}") from error

    if df.empty:
        raise ValueError(f"CSV file contains no data rows: {path}")

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
