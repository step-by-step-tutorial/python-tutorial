import pandas as pd

from sales_data_cleaning_service import SalesDataCleaningService
from sales_data_transformation_service import SalesDataTransformationService


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
    given_cleaning_service = SalesDataCleaningService()
    given_transformation_service = SalesDataTransformationService()
    given_cleaned_sales_dataframe = given_cleaning_service.clean_sales_data(
        given_sales_dataframe
    )
    given_transformed_sales_dataframe = (
        given_transformation_service.transform_sales_data(
            given_cleaned_sales_dataframe
        )
    )

    # When
    actual = given_transformation_service.build_sales_warehouse_dataframe(
        given_transformed_sales_dataframe
    )

    # Then
    assert "product_name" in actual.columns
    assert "product" not in actual.columns