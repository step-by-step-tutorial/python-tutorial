from dataclasses import asdict, dataclass
from typing import Any

from dataset.sale.columns import SALE_COLUMNS
from transformation.conversion.type_converter import convert_to_integer, convert_to_optional_float, \
    normalize_optional_text


@dataclass(frozen=True)
class SaleEvent:
    order_id: int
    customer_name: str
    product_name: str
    category: str
    quantity: float | None
    unit_price: float | None
    order_date: str | None
    country: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, row: dict[str, str]) -> "SaleEvent":
        return cls(
            order_id=convert_to_integer(row.get(SALE_COLUMNS.order_id)),
            customer_name=row[SALE_COLUMNS.customer_name],
            product_name=row[SALE_COLUMNS.product_name],
            category=row[SALE_COLUMNS.category],
            quantity=convert_to_optional_float(row.get(SALE_COLUMNS.quantity)),
            unit_price=convert_to_optional_float(row.get(SALE_COLUMNS.unit_price)),
            order_date=normalize_optional_text(row.get(SALE_COLUMNS.order_date)),
            country=row[SALE_COLUMNS.country]
        )
