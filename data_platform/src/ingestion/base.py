from __future__ import annotations

from abc import abstractmethod
from typing import Protocol, TypeVar

RawDataType = TypeVar("RawDataType")


class Ingestor(Protocol[RawDataType]):
    @abstractmethod
    def ingest(self) -> RawDataType:
        raise NotImplementedError
