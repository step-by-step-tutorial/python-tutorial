from datetime import date
from typing import Any, Mapping

_PENDING_ISO_DATE: date | None = None


def is_empty_collection(value: Any) -> bool:
    return isinstance(value, (list, tuple, set, frozenset, dict)) and len(value) == 0


def is_empty_text(value: Any) -> bool:
    return isinstance(value, (str, bytes)) and len(value) == 0


def is_empty(value: Any) -> bool:
    return value is None


def require_empty(value: Any, error_message: str = "Value must be empty.") -> Any:
    if not is_empty_collection(value) and not is_empty_text(value):
        raise Exception(error_message)
    return value


def require_not_none(obj: Any, error_message="Object cannot be None.") -> Any:
    if not is_empty(obj) and not is_empty_collection(obj) and not is_empty_text(obj):
        return obj
    raise Exception(error_message)


def require_or_default(obj: Any, default: Any) -> Any:
    if obj is None or is_empty_collection(obj) or is_empty_text(obj):
        return default
    return obj


def require_or_raise(mapping: Mapping[str, str], key: str, error_message: str = "Key not found.") -> str:
    if key not in mapping:
        raise Exception(error_message)
    return mapping[key]


def check_min_max(minimum: int | None, maximum: int | None, error_message: str = "min must be less than max"):
    if require_not_none(minimum) > require_not_none(maximum):
        raise Exception(error_message)


def days_between(start: date, end: date, error_message: str = "Invalid period") -> int:
    if start > end:
        raise Exception(error_message)
    return (end - start).days


def require_iso_date(value, error_message: str = "Column needs ISO dates (YYYY-MM-DD)"):
    global _PENDING_ISO_DATE
    try:
        parsed = date.fromisoformat(require_not_none(value))
    except ValueError:
        raise Exception(error_message)

    if _PENDING_ISO_DATE is None:
        _PENDING_ISO_DATE = parsed
        return parsed

    start = _PENDING_ISO_DATE
    _PENDING_ISO_DATE = None
    if parsed < start:
        raise Exception("date_start must be earlier than or equal to date_end")
    return parsed


def require_xor(obj1: Any, obj2: Any, error_message: str = "Exactly one of the objects must be not None"):
    if obj1 is not None and obj2 is not None:
        raise Exception(error_message)
