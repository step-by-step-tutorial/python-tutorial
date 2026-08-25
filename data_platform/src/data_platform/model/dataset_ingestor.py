from abc import ABC, abstractmethod
from typing import Any


class DatasetIngestor(ABC):
    name: str

    @abstractmethod
    def ingest(self) -> Any:
        raise NotImplementedError
