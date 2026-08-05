from dataclasses import asdict, dataclass
from typing import Any


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