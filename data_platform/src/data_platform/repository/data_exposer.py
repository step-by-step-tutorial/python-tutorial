from collections.abc import Callable
from typing import Any


class DataExposer:
    def __init__(self, persist_callbacks: tuple[Callable[[Any], Any], ...]) -> None:
        self._persist_callbacks = persist_callbacks

    def expose(self, data: Any) -> None:
        for persist_callback in self._persist_callbacks:
            persist_callback(data)
