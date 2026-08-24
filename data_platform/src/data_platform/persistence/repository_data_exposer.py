from collections.abc import Callable
from typing import Any


class RepositoryDataExposer:
    def __init__(self, *callbacks: Callable[[Any], Any]) -> None:
        # Accept the legacy loader/persist pair while exposing already-loaded data.
        self._persist_data = callbacks[-1]

    def expose(self, data: Any) -> None:
        self._persist_data(data)


