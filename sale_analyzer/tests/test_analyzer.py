import pandas as pd

from analyzer_service import (
    get_total_revenue,
    get_average_order_value,
    get_revenue_by_category,
    get_revenue_by_country,
)


def test_calculate_total_revenue():
    given_df = pd.DataFrame({
        "total_price": [100, 200, 300],
    })

    assert get_total_revenue(given_df) == 600


def test_calculate_average_order_value():
    given_df = pd.DataFrame({
        "total_price": [100, 200, 300],
    })

    assert get_average_order_value(given_df) == 200


def test_revenue_by_category():
    given_df = pd.DataFrame({
        "category": ["Electronics", "Furniture", "Electronics"],
        "total_price": [100, 300, 200],
    })

    actual = get_revenue_by_category(given_df)

    assert actual["Electronics"] == 300
    assert actual["Furniture"] == 300


def test_revenue_by_country():
    given_df = pd.DataFrame({
        "country": ["Germany", "USA", "Germany", "Iran"],
        "total_price": [100, 200, 300, 400],
    })

    actual = get_revenue_by_country(given_df)

    assert actual["Germany"] == 400
    assert actual["USA"] == 200
    assert actual["Iran"] == 400
