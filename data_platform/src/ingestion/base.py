from __future__ import annotations

from typing import Protocol, TypeVar

RawDataType = TypeVar("RawDataType")


class Ingestor(Protocol[RawDataType]):
    def ingest(self) -> RawDataType:
        raise NotImplementedError
