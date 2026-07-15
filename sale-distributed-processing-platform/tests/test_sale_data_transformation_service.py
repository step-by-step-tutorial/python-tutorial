
from src.sale_data_cleaning_service import SaleDataCleaningService
from src.sale_data_transformation_service import (
    SaleDataTransformationService,
)
from src.sale_schema import SALE_SCHEMA


def test_transform_sale_data_should_calculate_total_price(
    given_sale_spark_session,
):
    # Given
    given_sale_rows = [
        (
            1,
            "John",
            "Desk",
            "Furniture",
            2.0,
            300.0,
            "2026-01-07",
            "USA",
        ),
    ]
    given_sale_dataframe = given_sale_spark_session.createDataFrame(
        given_sale_rows,
        SALE_SCHEMA,
    )
    given_sale_data_cleaning_service = SaleDataCleaningService()
    given_sale_data_transformation_service = (
        SaleDataTransformationService()
    )
    given_cleaned_sale_dataframe = (
        given_sale_data_cleaning_service.clean_sale_data(
            given_sale_dataframe
        )
    )

    # When
    actual = given_sale_data_transformation_service.transform_sale_data(
        given_cleaned_sale_dataframe
    )

    # Then
    assert actual.first()["total_price"] == 600.0


def test_transform_sale_data_should_add_year_and_month(
    given_sale_spark_session,
):
    # Given
    given_sale_rows = [
        (
            1,
            "Anna",
            "Mouse",
            "Electronics",
            2.0,
            25.0,
            "2026-01-06",
            "Germany",
        ),
    ]
    given_sale_dataframe = given_sale_spark_session.createDataFrame(
        given_sale_rows,
        SALE_SCHEMA,
    )
    given_sale_data_cleaning_service = SaleDataCleaningService()
    given_sale_data_transformation_service = (
        SaleDataTransformationService()
    )
    given_cleaned_sale_dataframe = (
        given_sale_data_cleaning_service.clean_sale_data(
            given_sale_dataframe
        )
    )

    # When
    actual = given_sale_data_transformation_service.transform_sale_data(
        given_cleaned_sale_dataframe
    )

    # Then
    assert actual.first()["year"] == 2026
    assert actual.first()["month"] == 1


def test_build_sale_warehouse_dataframe_should_keep_expected_columns(
    given_sale_spark_session,
):
    # Given
    given_sale_rows = [
        (
            1,
            "Hans",
            "Laptop",
            "Electronics",
            1.0,
            1200.0,
            "2026-01-05",
            "Germany",
        ),
    ]
    given_sale_dataframe = given_sale_spark_session.createDataFrame(
        given_sale_rows,
        SALE_SCHEMA,
    )
    given_sale_data_cleaning_service = SaleDataCleaningService()
    given_sale_data_transformation_service = (
        SaleDataTransformationService()
    )
    given_cleaned_sale_dataframe = (
        given_sale_data_cleaning_service.clean_sale_data(
            given_sale_dataframe
        )
    )
    given_transformed_sale_dataframe = (
        given_sale_data_transformation_service.transform_sale_data(
            given_cleaned_sale_dataframe
        )
    )
    given_expected_columns = [
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

    # When
    actual = (
        given_sale_data_transformation_service
        .build_sale_warehouse_dataframe(
            given_transformed_sale_dataframe
        )
    )

    # Then
    assert actual.columns == given_expected_columns
