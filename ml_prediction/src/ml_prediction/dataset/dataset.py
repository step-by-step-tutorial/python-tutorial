from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class Dataset(ABC):
    def __init__(self, path: Path) -> None:
        self.path = path

    @abstractmethod
    def load(self) -> Any:
        ...
