TRUE_VALUES = frozenset({"1", "true", "yes", "on"})


def to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in TRUE_VALUES
