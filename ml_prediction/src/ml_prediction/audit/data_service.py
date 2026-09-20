from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class DataService(ABC):
    @abstractmethod
    def read(self, path: Path) -> Any:
        raise NotImplementedError

    @abstractmethod
    def write(self, data: Any, path: Path) -> None:
        raise NotImplementedError
