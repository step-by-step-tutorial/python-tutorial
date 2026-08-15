from collections.abc import Collection
from typing import Any, TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from pyspark.sql import DataFrame


def require_columns(df: pd.DataFrame, columns: frozenset[str]) -> None:
    if df is None or columns is None:
        raise ValueError("required columns or dataframe is None")

    missing_columns = columns.difference(df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")


def requires_column(df: Any, columns: Collection[str]) -> None:
    if df is None or columns is None:
        raise ValueError("required columns or dataframe is None")

    missing_columns = set(columns).difference(df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")
