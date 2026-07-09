from . import stub_data
from transform_service import transform_sales_data


def test_transform_sales_data_adds_total_price():
    given_df = stub_data.john_s_order()

    actual = transform_sales_data(given_df)

    assert actual.iloc[0]["total_price"] == 600


def test_transform_sales_data_adds_year_and_month():
    given_cleaned_df = stub_data.anna_s_order()

    actual = transform_sales_data(given_cleaned_df)

    assert actual.iloc[0]["year"] == 2026
    assert actual.iloc[0]["month"] == 1
