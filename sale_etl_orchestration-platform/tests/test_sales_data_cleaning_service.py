import pandas as pd

import clean_sale_data_util


def test_clean_sales_data_should_remove_invalid_order_date():
    # Given
    given_sales_dataframe = pd.DataFrame(
        {
            "order_id": [1, 2],
            "customer_name": ["Hans", "Pārsā"],
            "product": ["Laptop", "Chair"],
            "category": ["Electronics", "Furniture"],
            "quantity": [1, 2],
            "unit_price": [1200, 85],
            "order_date": ["2026-01-05", "invalid_date"],
            "country": ["Germany", "Iran"],
        }
    )

    # When
    actual = clean_sale_data_util.clean_sale_data(given_sales_dataframe)

    # Then
    assert len(actual) == 1
    assert actual.iloc[0]["order_id"] == 1


def test_clean_sales_data_should_fill_missing_quantity_with_one():
    # Given
    given_sales_dataframe = pd.DataFrame(
        {
            "order_id": [1],
            "customer_name": ["Ārman"],
            "product": ["Desk"],
            "category": ["Furniture"],
            "quantity": [None],
            "unit_price": [300],
            "order_date": ["2026-01-11"],
            "country": ["Iran"],
        }
    )
    # When
    actual = clean_sale_data_util.clean_sale_data(given_sales_dataframe)

    # Then
    assert actual.iloc[0]["quantity"] == 1