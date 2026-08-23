
from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from data_platform.model.house_attribute import HOUSE_ATTRIBUTE
from data_platform.model.sale_attribute import SALE_ATTRIBUTE
from data_platform.model.house_event import HouseEvent
from data_platform.model.sale_event import SaleEvent
from data_platform.converter.value_converter import (
    convert_to_integer,
    convert_to_float,
    convert_to_optional_float,
    convert_to_optional_boolean,
    normalize_optional_text,
)


@dataclass(frozen=True)
class MappedEvent:
    key: str | None
    payload: dict[str, Any]


class EventConverter(Protocol):
    def map(self, row: Mapping[str, Any]) -> MappedEvent:
        ...


@dataclass(frozen=True)
class SaleEventConverter:
    def map(self, row: Mapping[str, Any]) -> MappedEvent:
        event = SaleEvent(
            order_id=convert_to_integer(row.get(SALE_ATTRIBUTE.order_id)),
            customer_name=row[SALE_ATTRIBUTE.customer_name],
            product_name=row[SALE_ATTRIBUTE.product_name],
            category=row[SALE_ATTRIBUTE.category],
            quantity=convert_to_optional_float(row.get(SALE_ATTRIBUTE.quantity)),
            unit_price=convert_to_optional_float(row.get(SALE_ATTRIBUTE.unit_price)),
            order_date=normalize_optional_text(row.get(SALE_ATTRIBUTE.order_date)),
            country=row[SALE_ATTRIBUTE.country],
        )
        return MappedEvent(
            key=str(event.order_id),
            payload={
                SALE_ATTRIBUTE.order_id: event.order_id,
                SALE_ATTRIBUTE.customer_name: event.customer_name,
                SALE_ATTRIBUTE.product_name: event.product_name,
                SALE_ATTRIBUTE.category: event.category,
                SALE_ATTRIBUTE.quantity: event.quantity,
                SALE_ATTRIBUTE.unit_price: event.unit_price,
                SALE_ATTRIBUTE.order_date: event.order_date,
                SALE_ATTRIBUTE.country: event.country,
            },
        )


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


_EVENT_CONVERTERS: dict[str, EventConverter] = {
    "sale": SaleEventConverter(),
    "house": HouseEventConverter(),
}


def get_event_converter(dataset_name: str) -> EventConverter:
    try:
        return _EVENT_CONVERTERS[dataset_name.lower()]
    except KeyError as error:
        available = ", ".join(sorted(_EVENT_CONVERTERS)) or "<none>"
        raise KeyError(f"Unknown event mapper for dataset '{dataset_name}'. Available: {available}") from error
