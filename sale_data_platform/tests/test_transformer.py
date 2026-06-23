import pandas as pd

from cleaner_utils import clean_sales_data
from transformer import transform_sales_data


def test_transform_sales_data_adds_total_price():
    df = pd.DataFrame(
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

    cleaned_df = clean_sales_data(df)
    result = transform_sales_data(cleaned_df)

    assert result.iloc[0]["total_price"] == 600


def test_transform_sales_data_adds_year_and_month():
    df = pd.DataFrame(
        {
            "order_id": [1],
            "customer_name": ["Anna"],
            "product": ["Mouse"],
            "category": ["Electronics"],
            "quantity": [2],
            "unit_price": [25],
            "order_date": ["2026-01-06"],
            "country": ["Germany"],
        }
    )

    cleaned_df = clean_sales_data(df)
    result = transform_sales_data(cleaned_df)

    assert result.iloc[0]["year"] == 2026
    assert result.iloc[0]["month"] == 1