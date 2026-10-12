TRUE_VALUES = frozenset({"1", "true", "yes", "on"})


def to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in TRUE_VALUES


def to_optional_int(value: str | None) -> int | None:
    if value is None or value.strip() in {"", "0"}:
        return None
    return int(value)
