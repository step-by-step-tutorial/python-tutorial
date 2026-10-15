from collections import Counter
from collections.abc import Iterable
from typing import Any


def is_blank(value: Any) -> bool:
    if value is None:
        return True
    if hasattr(value, "empty"):
        return bool(value.empty)
    if isinstance(value, (str, bytes, list, tuple, set, frozenset, dict)):
        return len(value) == 0
    return False


def require_not_blank(value: Any, error_message: str) -> Any:
    if is_blank(value):
        raise ValueError(error_message)
    return value


def require_equal(actual: Any, expected: Any, error_message: str) -> None:
    if actual != expected:
        raise ValueError(error_message)


def require_unique(items: Iterable[str], error_message: str) -> None:
    duplicated = [item for item, count in Counter(items).items() if count > 1]
    if duplicated:
        raise ValueError(f"{error_message}: {duplicated}")


def require_columns(dataframe: Any, columns: Iterable[str], error_message: str) -> None:
    missing = [column for column in columns if column not in dataframe.columns]
    if missing:
        raise ValueError(f"{error_message}: {missing}")
