from collections.abc import Collection
from typing import Any


def validate_required_columns(df: Any, columns: Collection[str]) -> None:
    if df is None or columns is None:
        raise ValueError("required columns or dataframe is None")

    missing_columns = set(columns).difference(df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")
