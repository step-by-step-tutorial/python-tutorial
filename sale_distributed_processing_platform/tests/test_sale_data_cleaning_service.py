
from datetime import date

import pytest

from clean_sale_data_util import clean_sale_data
from app_config.sale_schema import SCHEMA


def test_clean_sale_data_should_remove_invalid_order_date(
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
        (
            2,
            "Pārsā",
            "Chair",
            "Furniture",
            2.0,
            85.0,
            "invalid_date",
            "Iran",
        ),
    ]
    given_sale_dataframe = given_sale_spark_session.createDataFrame(
        given_sale_rows,
        SCHEMA,
    )

    # When
    actual = clean_sale_data(
        given_sale_dataframe
    )

    # Then
    assert actual.count() == 1
    assert actual.first()["order_id"] == 1
    assert actual.first()["order_date"] == date(2026, 1, 5)


def test_clean_sale_data_should_fill_missing_quantity_with_one(
    given_sale_spark_session,
):
    # Given
    given_sale_rows = [
        (
            1,
            "Ārman",
            "Desk",
            "Furniture",
            None,
            300.0,
            "2026-01-11",
            "Iran",
        ),
    ]
    given_sale_dataframe = given_sale_spark_session.createDataFrame(
        given_sale_rows,
        SCHEMA,
    )

    # When
    actual = clean_sale_data(
        given_sale_dataframe
    )

    # Then
    assert actual.first()["quantity"] == 1.0


def test_clean_sale_data_should_raise_error_when_all_prices_are_missing(
    given_sale_spark_session,
):
    # Given
    given_sale_rows = [
        (
            1,
            "John",
            "Desk",
            "Furniture",
            1.0,
            None,
            "2026-01-07",
            "USA",
        ),
    ]
    given_sale_dataframe = given_sale_spark_session.createDataFrame(
        given_sale_rows,
        SCHEMA,
    )

    # When
    with pytest.raises(ValueError) as actual:
        clean_sale_data(
            given_sale_dataframe
        )

    # Then
    assert "unit_price" in str(actual.value)
