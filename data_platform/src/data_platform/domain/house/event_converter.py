from dataclasses import dataclass
from typing import Any, Mapping

from data_platform.converter.value_converter import (
    convert_to_float,
    convert_to_integer,
    convert_to_optional_boolean,
    convert_to_optional_float,
    normalize_optional_text,
)
from data_platform.domain.house.attribute import attribute
from data_platform.domain.house.event import HouseEvent
from data_platform.model.mapped_event import MappedEvent


@dataclass(frozen=True)
class HouseEventConverter:
    def map(self, row: Mapping[str, Any]) -> MappedEvent:
        event = HouseEvent(
            area=convert_to_float(row.get(attribute.area_raw)),
            room=convert_to_integer(row.get(attribute.room_raw)),
            parking=convert_to_optional_boolean(row.get(attribute.parking_raw)),
            warehouse=convert_to_optional_boolean(row.get(attribute.warehouse_raw)),
            elevator=convert_to_optional_boolean(row.get(attribute.elevator_raw)),
            address=normalize_optional_text(row.get(attribute.address_raw)),
            price=convert_to_float(row.get(attribute.price_raw)),
            price_usd=convert_to_optional_float(row.get(attribute.price_usd_raw)),
        )
        return MappedEvent(
            key=event.address,
            payload={
                attribute.area_raw: event.area,
                attribute.room_raw: event.room,
                attribute.parking_raw: event.parking,
                attribute.warehouse_raw: event.warehouse,
                attribute.elevator_raw: event.elevator,
                attribute.address_raw: event.address,
                attribute.price_raw: event.price,
                attribute.price_usd_raw: event.price_usd,
            },
        )


house_event_converter = HouseEventConverter()

