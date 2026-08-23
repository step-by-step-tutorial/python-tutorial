from dataclasses import dataclass


@dataclass(frozen=True)
class SaleAttribute:
    order_id: str = "order_id"
    customer_name: str = "customer_name"
    product_name: str = "product_name"
    category: str = "category"
    quantity: str = "quantity"
    unit_price: str = "unit_price"
    order_date: str = "order_date"
    country: str = "country"
    total_price: str = "total_price"
    year: str = "year"
    month: str = "month"
    revenue: str = "revenue"

    def __getattr__(self, item: str) -> str:
        lowered = item.lower()
        try:
            return object.__getattribute__(self, lowered)
        except Exception as error:
            raise AttributeError(item) from error


SALE_ATTRIBUTE = SaleAttribute()
