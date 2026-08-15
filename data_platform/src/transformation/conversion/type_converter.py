from typing import Any


def convert_to_integer(value: str | None) -> int:
    if value is None or value.strip() == "":
        raise ValueError("Cannot convert an empty value to integer.")

    return int(value)


def convert_to_optional_float(value: str | None) -> float | None:
    if value is None or value.strip() == "":
        return None

    try:
        return float(value)
    except ValueError:
        return None


def normalize_optional_text(value: Any) -> str | None:
    if value is None:
        return None

    normalized_value = str(value).strip()

    if normalized_value == "":
        return None

    return normalized_value
