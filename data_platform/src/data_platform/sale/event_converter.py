from dataclasses import dataclass
from typing import Any, Mapping

from data_platform.converter.value_converter import (
    convert_to_integer,
    convert_to_optional_float,
    normalize_optional_text,
)
from data_platform.model.mapped_event import MappedEvent
from data_platform.sale.attribute import SALE_ATTRIBUTE
from data_platform.sale.event import SaleEvent
from data_platform.registry.event_converter_registry import event_converter_registry


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


sale_event_converter = SaleEventConverter()


def register_sale_event_converter() -> None:
    if not event_converter_registry.contains("sale"):
        event_converter_registry.register("sale", sale_event_converter)
