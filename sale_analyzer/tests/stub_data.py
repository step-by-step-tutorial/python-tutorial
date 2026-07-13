import pandas as pd
from clean_data_service import clean_sale_data


def john_s_order() -> pd.DataFrame:
    order = pd.DataFrame({
        "order_id": [1],
        "customer_name": ["John"],
        "product": ["Desk"],
        "category": ["Furniture"],
        "quantity": [2],
        "unit_price": [300],
        "order_date": ["2026-01-07"],
        "country": ["USA"],
    })

    return clean_sale_data(order)


def anna_s_order() -> pd.DataFrame:
    order = pd.DataFrame({
        "order_id": [1],
        "customer_name": ["Anna"],
        "product": ["Mouse"],
        "category": ["Electronics"],
        "quantity": [2],
        "unit_price": [25],
        "order_date": ["2026-01-06"],
        "country": ["Germany"],
    })

    return clean_sale_data(order)
