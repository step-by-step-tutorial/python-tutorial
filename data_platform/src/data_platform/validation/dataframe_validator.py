from collections.abc import Collection
from typing import Any

from data_platform.util.string_utils import should_not_be_none


def validate_required_columns(df: Any, columns: Collection[str]) -> None:
    should_not_be_none(df, "dataframe")
    should_not_be_none(columns, "required columns")

    missing_columns = set(columns).difference(df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

