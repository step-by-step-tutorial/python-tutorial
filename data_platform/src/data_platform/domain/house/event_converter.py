from dataclasses import dataclass
from typing import Any, Mapping

from data_platform.domain.house.attribute import attribute
from data_platform.domain.house.event import HouseEvent
from data_platform.model.mapped_event import MappedEvent


@dataclass(frozen=True)
class HouseEventConverter:
    def map(self, row: Mapping[str, Any]) -> MappedEvent:
        values = {column: row.get(column) for column in attribute.columns}
        event = HouseEvent(values)
        return MappedEvent(key=event.property_id, payload=event.to_dict())


house_event_converter = HouseEventConverter()
