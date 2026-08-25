from dataclasses import dataclass
from typing import Any, Mapping

from data_platform.converter.value_converter import (
    convert_to_integer,
    convert_to_optional_float,
    normalize_optional_text,
)
from data_platform.domain.sale.attribute import attribute
from data_platform.domain.sale.event import SaleEvent
from data_platform.model.mapped_event import MappedEvent


@dataclass(frozen=True)
class SaleEventConverter:
    def map(self, row: Mapping[str, Any]) -> MappedEvent:
        event = SaleEvent(
            order_id=convert_to_integer(row.get(attribute.order_id)),
            customer_name=row[attribute.customer_name],
            product_name=row[attribute.product_name],
            category=row[attribute.category],
            quantity=convert_to_optional_float(row.get(attribute.quantity)),
            unit_price=convert_to_optional_float(row.get(attribute.unit_price)),
            order_date=normalize_optional_text(row.get(attribute.order_date)),
            country=row[attribute.country],
        )
        return MappedEvent(
            key=str(event.order_id),
            payload={
                attribute.order_id: event.order_id,
                attribute.customer_name: event.customer_name,
                attribute.product_name: event.product_name,
                attribute.category: event.category,
                attribute.quantity: event.quantity,
                attribute.unit_price: event.unit_price,
                attribute.order_date: event.order_date,
                attribute.country: event.country,
            },
        )


sale_event_converter = SaleEventConverter()

