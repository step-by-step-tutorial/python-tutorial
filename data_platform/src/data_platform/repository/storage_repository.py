from typing import Any, Protocol


class StorageRepository(Protocol):
    def save(self, data: Any, path: str) -> str:
        ...

    def find(self, path: str) -> Any:
        ...
