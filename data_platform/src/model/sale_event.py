from dataclasses import asdict, dataclass
from typing import Any

from app_config.dataframe_schema import SALE_COLUMNS
from util.csv_utils import convert_to_integer, convert_to_optional_float, normalize_optional_text


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
            order_id=convert_to_integer(row.get(SALE_COLUMNS.ORDER_ID)),
            customer_name=row[SALE_COLUMNS.CUSTOMER_NAME],
            product_name=row[SALE_COLUMNS.PRODUCT_NAME],
            category=row[SALE_COLUMNS.CATEGORY],
            quantity=convert_to_optional_float(row.get(SALE_COLUMNS.QUANTITY)),
            unit_price=convert_to_optional_float(row.get(SALE_COLUMNS.UNIT_PRICE)),
            order_date=normalize_optional_text(row.get(SALE_COLUMNS.ORDER_DATE)),
            country=row[SALE_COLUMNS.COUNTRY]
        )