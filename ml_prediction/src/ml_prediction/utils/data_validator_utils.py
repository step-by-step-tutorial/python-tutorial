from collections import Counter
from collections.abc import Collection
from datetime import date
from typing import Any, Mapping, Iterable


def is_empty_collection(obj: Any) -> bool:
    return isinstance(obj, (list, tuple, set, frozenset, dict)) and len(obj) == 0


def is_empty_text(obj: Any) -> bool:
    return isinstance(obj, (str, bytes)) and len(obj) == 0


def is_none(obj: Any) -> bool:
    return obj is None


def is_not_none(obj: Any) -> bool:
    return obj is not None


def is_blank(obj: Any) -> bool:
    return is_none(obj) or is_empty_collection(obj) or is_empty_text(obj)


def is_not_blank(obj: Any) -> bool:
    if hasattr(obj, "empty"):
        return not obj.empty
    return not is_blank(obj)


def should_be_blank(value: Any, error_message: str = "Value must be empty.") -> Any:
    if not is_blank(value):
        raise Exception(error_message)
    return value


def should_not_be_blank(obj: Any, error_message="Object cannot be None.") -> Any:
    if is_blank(obj):
        raise Exception(error_message)
    return obj


def should_be_same(first: Any, second: Any, error_message: str = "Values must be the same.") -> None:
    if isinstance(first, Collection) and isinstance(second, Collection) and not isinstance(first, (str, bytes)):
        difference = sorted(set(first).difference(second))
        if difference:
            raise Exception(error_message.format(difference=difference))
        return
    if first != second:
        raise Exception(error_message)


def value_or_default(obj: Any, default: Any) -> Any:
    if is_blank(obj):
        return default
    return obj


def should_have_key_in_map(mapping: Mapping[str, Any], key: str, error_message: str = "Key not found.") -> Any:
    if key not in mapping:
        raise Exception(error_message)
    return mapping[key]


def should_have_key_in_tuple(collection: tuple[str, ...], key: str, error_message: str = "Key not found.") -> str:
    if key not in collection:
        raise Exception(error_message)
    return collection[collection.index(key)]


def should_be_absent(collection: tuple[str, ...], key: str, error_message: str = "Key not found."):
    if key in collection:
        raise Exception(error_message)


def check_min_max(minimum: int | None, maximum: int | None, error_message: str = "min must be less than max"):
    if should_not_be_blank(minimum) > should_not_be_blank(maximum):
        raise Exception(error_message)


def check_negative_days(start: date, end: date, error_message: str = "Invalid period") -> int:
    if start > end:
        raise Exception(error_message)
    return (end - start).days


def should_be_iso_date(value, error_message: str = "Column needs ISO dates (YYYY-MM-DD)"):
    try:
        parsed = date.fromisoformat(should_not_be_blank(value))
    except ValueError:
        raise Exception(error_message)

    return parsed


def should_be_xor(obj1: Any, obj2: Any, error_message: str = "Exactly one of the objects must be not None"):
    if (is_blank(obj1) and is_blank(obj2)) or (not is_blank(obj1) and not is_blank(obj2)):
        raise Exception(error_message)


def should_not_be_negative(*numbers: int, error_message: str = "Value must not be negative"):
    for number in numbers:
        if number < 0:
            raise Exception(error_message)


def should_have_same_columns(
    dataframe: Any,
    columns: Iterable[str],
    message: str = "Missing required columns",
) -> None:
    missing = find_missing_columns(dataframe, columns)
    if missing:
        raise ValueError(f"{message}: {', '.join(missing)}")


def find_missing_columns(dataframe: Any, columns: Iterable[str]) -> tuple[str, ...]:
    return tuple(column for column in columns if column not in dataframe.columns)


def should_not_have_duplication(items: list[str]) -> None:
    duplicated = [column for column, count in Counter(items).items() if count > 1]
    should_be_blank(duplicated, f"Duplicated feature column features: {duplicated}")
