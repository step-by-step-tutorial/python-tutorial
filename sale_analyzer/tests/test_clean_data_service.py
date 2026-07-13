import pandas as pd

from clean_sale_data_util import clean_sale_data


def test_clean_sale_data_removes_invalid_date():
    given_df = pd.DataFrame({
        "order_id": [1, 2],
        "customer_name": ["Hans", "Pārsā"],
        "product": ["Laptop", "Chair"],
        "category": ["Electronics", "Furniture"],
        "quantity": [1, 2],
        "unit_price": [1200, 85],
        "order_date": ["2026-01-05", "invalid_date"],
        "country": ["Germany", "Iran"],
    })

    actual = clean_sale_data(given_df)

    assert len(actual) == 1
    assert actual.iloc[0]["order_id"] == 1


def test_clean_sale_data_fills_missing_quantity_with_one():
    given_df = pd.DataFrame({
        "order_id": [1],
        "customer_name": ["Ārman"],
        "product": ["Desk"],
        "category": ["Furniture"],
        "quantity": [None],
        "unit_price": [300],
        "order_date": ["2026-01-11"],
        "country": ["Iran"],
    })

    actual = clean_sale_data(given_df)

    assert actual.iloc[0]["quantity"] == 1
