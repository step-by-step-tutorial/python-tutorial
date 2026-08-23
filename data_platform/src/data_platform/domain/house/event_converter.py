from dataclasses import dataclass
from typing import Any, Mapping

from data_platform.converter.value_converter import (
    convert_to_float,
    convert_to_integer,
    convert_to_optional_boolean,
    convert_to_optional_float,
    normalize_optional_text,
)
from data_platform.domain.house.attribute import HOUSE_ATTRIBUTE
from data_platform.domain.house.event import HouseEvent
from data_platform.model.mapped_event import MappedEvent
from data_platform.registry.event_converter_registry import event_converter_registry


@dataclass(frozen=True)
class HouseEventConverter:
    def map(self, row: Mapping[str, Any]) -> MappedEvent:
        event = HouseEvent(
            area=convert_to_float(row.get(HOUSE_ATTRIBUTE.area_raw)),
            room=convert_to_integer(row.get(HOUSE_ATTRIBUTE.room_raw)),
            parking=convert_to_optional_boolean(row.get(HOUSE_ATTRIBUTE.parking_raw)),
            warehouse=convert_to_optional_boolean(row.get(HOUSE_ATTRIBUTE.warehouse_raw)),
            elevator=convert_to_optional_boolean(row.get(HOUSE_ATTRIBUTE.elevator_raw)),
            address=normalize_optional_text(row.get(HOUSE_ATTRIBUTE.address_raw)),
            price=convert_to_float(row.get(HOUSE_ATTRIBUTE.price_raw)),
            price_usd=convert_to_optional_float(row.get(HOUSE_ATTRIBUTE.price_usd_raw)),
        )
        return MappedEvent(
            key=event.address,
            payload={
                HOUSE_ATTRIBUTE.area_raw: event.area,
                HOUSE_ATTRIBUTE.room_raw: event.room,
                HOUSE_ATTRIBUTE.parking_raw: event.parking,
                HOUSE_ATTRIBUTE.warehouse_raw: event.warehouse,
                HOUSE_ATTRIBUTE.elevator_raw: event.elevator,
                HOUSE_ATTRIBUTE.address_raw: event.address,
                HOUSE_ATTRIBUTE.price_raw: event.price,
                HOUSE_ATTRIBUTE.price_usd_raw: event.price_usd,
            },
        )


house_event_converter = HouseEventConverter()


def register_house_event_converter() -> None:
    if not event_converter_registry.contains("house"):
        event_converter_registry.register("house", house_event_converter)
