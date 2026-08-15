from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from dataset.house.columns import HOUSE_COLUMNS as house_columns
from dataset.sale.columns import SALE_COLUMNS as sale_columns
from model.house_event import HouseEvent
from model.sale_event import SaleEvent
from transformation.conversion.type_converter import (
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


class EventMapper(Protocol):
    def map(self, row: dict[str, str]) -> MappedEvent:
        ...


@dataclass(frozen=True)
class SaleEventMapper:
    def map(self, row: dict[str, str]) -> MappedEvent:
        event = SaleEvent(
            order_id=convert_to_integer(row.get(sale_columns.order_id)),
            customer_name=row[sale_columns.customer_name],
            product_name=row[sale_columns.product_name],
            category=row[sale_columns.category],
            quantity=convert_to_optional_float(row.get(sale_columns.quantity)),
            unit_price=convert_to_optional_float(row.get(sale_columns.unit_price)),
            order_date=normalize_optional_text(row.get(sale_columns.order_date)),
            country=row[sale_columns.country],
        )
        return MappedEvent(
            key=str(event.order_id),
            payload={
                sale_columns.order_id: event.order_id,
                sale_columns.customer_name: event.customer_name,
                sale_columns.product_name: event.product_name,
                sale_columns.category: event.category,
                sale_columns.quantity: event.quantity,
                sale_columns.unit_price: event.unit_price,
                sale_columns.order_date: event.order_date,
                sale_columns.country: event.country,
            },
        )


@dataclass(frozen=True)
class HouseEventMapper:
    def map(self, row: dict[str, str]) -> MappedEvent:
        event = HouseEvent(
            area=convert_to_float(row.get(house_columns.area_raw)),
            room=convert_to_integer(row.get(house_columns.room_raw)),
            parking=convert_to_optional_boolean(row.get(house_columns.parking_raw)),
            warehouse=convert_to_optional_boolean(row.get(house_columns.warehouse_raw)),
            elevator=convert_to_optional_boolean(row.get(house_columns.elevator_raw)),
            address=normalize_optional_text(row.get(house_columns.address_raw)),
            price=convert_to_float(row.get(house_columns.price_raw)),
            price_usd=convert_to_optional_float(row.get(house_columns.price_usd_raw)),
        )
        return MappedEvent(
            key=event.address,
            payload={
                house_columns.area_raw: event.area,
                house_columns.room_raw: event.room,
                house_columns.parking_raw: event.parking,
                house_columns.warehouse_raw: event.warehouse,
                house_columns.elevator_raw: event.elevator,
                house_columns.address_raw: event.address,
                house_columns.price_raw: event.price,
                house_columns.price_usd_raw: event.price_usd,
            },
        )


_EVENT_MAPPERS: dict[str, EventMapper] = {
    "sale": SaleEventMapper(),
    "house": HouseEventMapper(),
}


def get_event_mapper(dataset_name: str) -> EventMapper:
    try:
        return _EVENT_MAPPERS[dataset_name.lower()]
    except KeyError as error:
        available = ", ".join(sorted(_EVENT_MAPPERS)) or "<none>"
        raise KeyError(f"Unknown event mapper for dataset '{dataset_name}'. Available: {available}") from error
