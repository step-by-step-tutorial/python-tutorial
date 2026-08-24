from dataclasses import dataclass


@dataclass(frozen=True)
class OnlineShoppingAttribute:
    order_id: str = "order_id"
    order_date: str = "order_date"
    sales_channel: str = "sales_channel"
    customer_id: str = "customer_id"
    first_name: str = "first_name"
    last_name: str = "last_name"
    email: str = "email"
    phone: str = "phone"
    shipping_address: str = "shipping_address"
    country: str = "country"
    currency: str = "currency"
    warehouse: str = "warehouse"
    product_name: str = "product_name"
    category: str = "category"
    unit_price: str = "unit_price"
    quantity: str = "quantity"
    subtotal: str = "subtotal"
    discount_percent: str = "discount_percent"
    shipping_cost: str = "shipping_cost"
    tax_amount: str = "tax_amount"
    total_amount: str = "total_amount"
    payment_status: str = "payment_status"
    fulfillment_status: str = "fulfillment_status"
    estimated_delivery_date: str = "estimated_delivery_date"
    coupon_code: str = "coupon_code"
    payment_method: str = "payment_method"
    shipping_method: str = "shipping_method"
    delivery_days: str = "delivery_days"
    order_status: str = "order_status"
    discount_amount: str = "discount_amount"
    net_revenue: str = "net_revenue"
    year: str = "year"
    month: str = "month"
    revenue: str = "revenue"


ONLINE_SHOPPING_ATTRIBUTE = OnlineShoppingAttribute()

