import pandas as pd

from clean_sale_data_util import clean_sale_data
from transform_sale_data_util import transform_sale_data
from transform_sale_fact_util import transform_sale_fact


def test_build_warehouse_dataframe_renames_product_to_product_name():
    df = pd.DataFrame(
        {
            "order_id": [1],
            "customer_name": ["Hans"],
            "product": ["Laptop"],
            "category": ["Electronics"],
            "quantity": [1],
            "unit_price": [1200],
            "order_date": ["2026-01-05"],
            "country": ["Germany"],
        }
    )

    cleaned_df = clean_sale_data(df)
    transformed_df = transform_sale_data(cleaned_df)
    warehouse_df = transform_sale_fact(transformed_df)

    assert "product_name" in warehouse_df.columns
    assert "product" not in warehouse_df.columns


def test_build_warehouse_dataframe_has_required_columns():
    df = pd.DataFrame(
        {
            "order_id": [1],
            "customer_name": ["John"],
            "product": ["Desk"],
            "category": ["Furniture"],
            "quantity": [1],
            "unit_price": [300],
            "order_date": ["2026-01-07"],
            "country": ["USA"],
        }
    )

    cleaned_df = clean_sale_data(df)
    transformed_df = transform_sale_data(cleaned_df)
    warehouse_df = transform_sale_fact(transformed_df)

    expected_columns = [
        "order_id",
        "customer_name",
        "product_name",
        "category",
        "country",
        "quantity",
        "unit_price",
        "total_price",
        "order_date",
        "year",
        "month",
    ]

    assert list(warehouse_df.columns) == expected_columns