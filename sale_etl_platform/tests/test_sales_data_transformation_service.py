import pandas as pd

import clean_sale_data_util
import transform_sale_data_util


def test_transform_sales_data_should_add_total_price():
    # Given
    given_sales_dataframe = pd.DataFrame(
        {
            "order_id": [1],
            "customer_name": ["John"],
            "product": ["Desk"],
            "category": ["Furniture"],
            "quantity": [2],
            "unit_price": [300],
            "order_date": ["2026-01-07"],
            "country": ["USA"],
        }
    )
    given_cleaned_sales_dataframe = clean_sale_data_util.clean_sale_data(given_sales_dataframe)

    # When
    actual = transform_sale_data_util.transform_sale_data(given_cleaned_sales_dataframe)

    # Then
    assert actual.iloc[0]["total_price"] == 600