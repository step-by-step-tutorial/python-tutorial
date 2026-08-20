from datetime import date
from typing import Any, Mapping

_PENDING_ISO_DATE: date | None = None


def is_empty_collection(obj: Any) -> bool:
    return isinstance(obj, (list, tuple, set, frozenset, dict)) and len(obj) == 0


def is_empty_text(obj: Any) -> bool:
    return isinstance(obj, (str, bytes)) and len(obj) == 0


def is_none(obj: Any) -> bool:
    return obj is None


def is_none_or_empty(obj: Any) -> bool:
    return is_none(obj) or is_empty_collection(obj) or is_empty_text(obj)


def require_empty(value: Any, error_message: str = "Value must be empty.") -> Any:
    if not is_none_or_empty(value):
        raise Exception(error_message)
    return value


def require_not_none(obj: Any, error_message="Object cannot be None.") -> Any:
    if is_none_or_empty(obj):
        raise Exception(error_message)
    return obj


def require_or_default(obj: Any, default: Any) -> Any:
    if is_none_or_empty(obj):
        return default
    return obj


def require_or_raise(mapping: Mapping[str, str], key: str, error_message: str = "Key not found.") -> str:
    if key not in mapping:
        raise Exception(error_message)
    return mapping[key]


def check_min_max(minimum: int | None, maximum: int | None, error_message: str = "min must be less than max"):
    if require_not_none(minimum) > require_not_none(maximum):
        raise Exception(error_message)


def check_negative_days(start: date, end: date, error_message: str = "Invalid period") -> int:
    if start > end:
        raise Exception(error_message)
    return (end - start).days


def require_iso_date(value, error_message: str = "Column needs ISO dates (YYYY-MM-DD)"):
    try:
        parsed = date.fromisoformat(require_not_none(value))
    except ValueError:
        raise Exception(error_message)

    return parsed


def require_xor(obj1: Any, obj2: Any, error_message: str = "Exactly one of the objects must be not None"):
    if obj1 is not None and obj2 is not None:
        raise Exception(error_message)
