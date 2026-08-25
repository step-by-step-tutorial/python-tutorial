from typing import Any, Protocol


class StorageRepository(Protocol):
    def write(self, data: Any, path: str) -> str:
        ...

    def read(self, path: str) -> Any:
        ...
