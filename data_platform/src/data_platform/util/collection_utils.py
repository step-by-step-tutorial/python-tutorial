from collections.abc import Mapping


def to_values(mapping: Mapping) -> list[str]:
    return [str(item) for item in mapping.values()]


def to_batches(rows: list[tuple[object, ...]], batch_size: int = 1000) -> list[list[tuple[object, ...]]]:
    return [rows[index: index + batch_size] for index in range(0, len(rows), batch_size)]
