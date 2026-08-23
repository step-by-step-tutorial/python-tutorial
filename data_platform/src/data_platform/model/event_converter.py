from typing import Any, Mapping, Protocol

from data_platform.model.mapped_event import MappedEvent


class EventConverter(Protocol):
    def map(self, row: Mapping[str, Any]) -> MappedEvent:
        ...
