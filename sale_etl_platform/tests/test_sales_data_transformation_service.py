import pandas as pd

from sales_data_cleaning_service import SalesDataCleaningService
from sales_data_transformation_service import SalesDataTransformationService


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
    given_cleaning_service = SalesDataCleaningService()
    given_transformation_service = SalesDataTransformationService()
    given_cleaned_sales_dataframe = given_cleaning_service.clean_sales_data(
        given_sales_dataframe
    )

    # When
    actual = given_transformation_service.transform_sales_data(
        given_cleaned_sales_dataframe
    )

    # Then
    assert actual.iloc[0]["total_price"] == 600