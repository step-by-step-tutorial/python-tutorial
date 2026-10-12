from collections.abc import Mapping
from datetime import date
from typing import Any


def is_blank(value: Any) -> bool:
    """None, an empty string or an empty collection."""
    return value is None or (isinstance(value, (str, bytes, list, tuple, set, frozenset, dict)) and len(value) == 0)


def default_if_blank(value: Any, default: Any) -> Any:
    return default if is_blank(value) else value


def require_blank(value: Any, error_message: str = "Value must be blank.") -> Any:
    if not is_blank(value):
        raise ValueError(error_message)
    return value


def require_not_blank(value: Any, error_message: str = "Value must not be blank.") -> Any:
    if is_blank(value):
        raise ValueError(error_message)
    return value


def require_key(mapping: Mapping[str, Any], key: str, error_message: str = "Key not found.") -> Any:
    if key not in mapping:
        raise KeyError(error_message)
    return mapping[key]


def require_exactly_one(first: Any, second: Any, error_message: str = "Exactly one of the values must be set.") -> None:
    if is_blank(first) == is_blank(second):
        raise ValueError(error_message)


def require_not_greater(minimum: int, maximum: int, error_message: str = "min must not be greater than max") -> None:
    if require_not_blank(minimum) > require_not_blank(maximum):
        raise ValueError(error_message)


def require_not_negative(*numbers: int, error_message: str = "Value must not be negative") -> None:
    if any(number < 0 for number in numbers):
        raise ValueError(error_message)


def require_iso_date(value: str | None, error_message: str = "Column needs ISO dates (YYYY-MM-DD)") -> date:
    try:
        return date.fromisoformat(require_not_blank(value))
    except ValueError as error:
        raise ValueError(error_message) from error
