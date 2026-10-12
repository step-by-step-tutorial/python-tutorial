from collections.abc import Iterable, Mapping
from datetime import date
from typing import Any

from data_platform.util.dataframe_utils import find_missing_columns


def is_empty_collection(obj: Any) -> bool:
    return isinstance(obj, (list, tuple, set, frozenset, dict)) and len(obj) == 0


def is_empty_text(obj: Any) -> bool:
    return isinstance(obj, (str, bytes)) and len(obj) == 0


def is_none(obj: Any) -> bool:
    return obj is None


def is_blank(obj: Any) -> bool:
    return is_none(obj) or is_empty_collection(obj) or is_empty_text(obj)


def is_not_blank(obj: Any) -> bool:
    if hasattr(obj, "empty"):
        return not obj.empty
    return not is_blank(obj)


def default_if_blank(obj: Any, default: Any) -> Any:
    return default if is_blank(obj) else obj


def require_not_none(value: Any, name: str) -> Any:
    if value is None:
        raise ValueError(f"Value of {name} should not be None")
    return value


def require_not_empty(value: Any, name: str) -> Any:
    if value is None or not str(value).strip():
        raise ValueError(f"Value of {name} should not be None or empty")
    return value


def require_blank(value: Any, error_message: str = "Value must be empty.") -> Any:
    if not is_blank(value):
        raise ValueError(error_message)
    return value


def require_not_blank(obj: Any, error_message: str = "Object cannot be None.") -> Any:
    if is_blank(obj):
        raise ValueError(error_message)
    return obj


def require_key(mapping: Mapping[str, Any], key: str, error_message: str = "Key not found.") -> Any:
    if key not in mapping:
        raise ValueError(error_message)
    return mapping[key]


def require_item(collection: tuple[str, ...], key: str, error_message: str = "Key not found.") -> str:
    if key not in collection:
        raise ValueError(error_message)
    return collection[collection.index(key)]


def require_absent(collection: tuple[str, ...], key: str, error_message: str = "Key already exists.") -> None:
    if key in collection:
        raise ValueError(error_message)


def require_min_max(minimum: int | None, maximum: int | None,
                    error_message: str = "min must be less than max") -> None:
    if require_not_blank(minimum) > require_not_blank(maximum):
        raise ValueError(error_message)


def require_period_days(start: date, end: date, error_message: str = "Invalid period") -> int:
    if start > end:
        raise ValueError(error_message)
    return (end - start).days


def require_iso_date(value: Any, error_message: str = "Column needs ISO dates (YYYY-MM-DD)") -> date:
    try:
        return date.fromisoformat(require_not_blank(value))
    except ValueError as error:
        raise ValueError(error_message) from error


def require_xor(obj1: Any, obj2: Any, error_message: str = "Exactly one of the objects must be not None") -> None:
    if is_blank(obj1) == is_blank(obj2):
        raise ValueError(error_message)


def require_not_negative(*numbers: int, error_message: str = "Value must not be negative") -> None:
    for number in numbers:
        if number < 0:
            raise ValueError(error_message)


def require_columns(dataframe: Any, columns: Iterable[str], message: str = "Missing required columns") -> None:
    missing = find_missing_columns(dataframe, columns)
    if missing:
        raise ValueError(f"{message}: {', '.join(missing)}")
