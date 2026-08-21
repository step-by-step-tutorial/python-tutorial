from collections.abc import Callable


def order_dependencies(
        original: tuple[str, ...],
        consumer: Callable[[str, tuple[str, ...], list[str], list[str]], None]
) -> tuple[str, ...]:
    ordered: list[str] = []
    resolved: list[str] = []

    for name in original:
        pending = ()
        consumer(name, pending, resolved, ordered)

    return tuple(ordered)
