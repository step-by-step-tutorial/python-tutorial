import pandas as pd

import clean_sale_data_util
import transform_sale_data_util
import transform_sale_fact_util


def test_build_sales_warehouse_dataframe_should_rename_product_to_product_name():
    # Given
    given_sales_dataframe = pd.DataFrame(
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
    given_cleaned_sales_dataframe = clean_sale_data_util.clean_sale_data(given_sales_dataframe)
    given_transformed_sales_dataframe = transform_sale_data_util.transform_sale_data(given_cleaned_sales_dataframe)

    # When
    actual = transform_sale_fact_util.transform_sale_fact(given_transformed_sales_dataframe)

    # Then
    assert "product_name" in actual.columns
    assert "product" not in actual.columns