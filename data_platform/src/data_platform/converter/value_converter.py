from math import isnan
from typing import Any


def _normalize_text(value: Any) -> str:
    return str(value).strip()


def _normalize_numeric_text(value: Any) -> str:
    return _normalize_text(value).replace(",", "")


def _is_missing(value: Any) -> bool:
    if value is None:
        return True

    if isinstance(value, float):
        return isnan(value)

    return False


def convert_to_integer(value: Any) -> int:
    if _is_missing(value):
        raise ValueError("Cannot convert an empty value to integer.")

    if isinstance(value, bool):
        return int(value)

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        raise ValueError(f"Cannot convert a non-integer float to integer: {value}")

    if _normalize_text(value) == "":
        raise ValueError("Cannot convert an empty value to integer.")

    return int(value)


def convert_to_optional_float(value: Any) -> float | None:
    if _is_missing(value):
        return None

    if isinstance(value, bool):
        return float(int(value))

    if isinstance(value, (int, float)):
        return float(value)

    normalized_value = _normalize_numeric_text(value)
    if normalized_value == "":
        return None

    try:
        return float(normalized_value)
    except Exception:
        return None


def convert_to_float(value: Any) -> float:
    if _is_missing(value):
        raise ValueError("Cannot convert an empty value to float.")

    if isinstance(value, bool):
        return float(int(value))

    if isinstance(value, (int, float)):
        return float(value)

    normalized_value = _normalize_numeric_text(value)
    if normalized_value == "":
        raise ValueError("Cannot convert an empty value to float.")

    try:
        return float(normalized_value)
    except Exception as error:
        raise ValueError(f"Cannot convert value to float: {value}") from error


def normalize_optional_text(value: Any) -> str | None:
    if _is_missing(value):
        return None

    normalized_value = _normalize_text(value)

    if normalized_value == "":
        return None

    return normalized_value


def convert_to_optional_boolean(value: Any) -> bool | None:
    if _is_missing(value):
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return bool(value)

    normalized_value = _normalize_text(value).lower()
    if normalized_value == "":
        return None
    if normalized_value in {"true", "1", "yes", "y"}:
        return True
    if normalized_value in {"false", "0", "no", "n"}:
        return False

    raise ValueError(f"Cannot convert value to boolean: {value}")
