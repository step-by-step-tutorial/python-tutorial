from datetime import date
from typing import Any, Mapping


def require_not_none(obj: Any, error_message="Object cannot be None.") -> Any:
    if not obj or obj is None:
        raise ValueError(error_message)
    return obj


def require_or_default(obj: Any, default: Any) -> Any:
    if not obj or obj is None:
        return default
    return obj


def require_or_raise(mapping: Mapping[str, str], key: str, error_message: str = "Key not found.") -> str:
    try:
        return mapping[key]
    except Exception:
        raise ValueError(error_message)


def check_min_max(minimum: int | None, maximum: int | None, error_message: str = "min must be less than max"):
    if require_not_none(minimum) > require_not_none(maximum):
        raise ValueError(error_message)


def require_iso_date(value, error_message: str = "Date must be in ISO format (YYYY-MM-DD)"):
    try:
        return date.fromisoformat(require_not_none(value))
    except ValueError:
        raise ValueError(error_message)


def require_xor(obj1: Any, obj2: Any, error_message: str = "Exactly one of the objects must be not None"):
    if obj1 and obj2:
        raise ValueError(error_message)
