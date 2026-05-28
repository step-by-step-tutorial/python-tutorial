import pandas as pd

from app.analyzer import (
    calculate_total_revenue,
    calculate_average_order_value,
    revenue_by_category,
    revenue_by_country,
)


def test_calculate_total_revenue():
    df = pd.DataFrame({
        "total_price": [100, 200, 300],
    })

    assert calculate_total_revenue(df) == 600


def test_calculate_average_order_value():
    df = pd.DataFrame({
        "total_price": [100, 200, 300],
    })

    assert calculate_average_order_value(df) == 200


def test_revenue_by_category():
    df = pd.DataFrame({
        "category": ["Electronics", "Furniture", "Electronics"],
        "total_price": [100, 300, 200],
    })

    result = revenue_by_category(df)

    assert result["Electronics"] == 300
    assert result["Furniture"] == 300


def test_revenue_by_country():
    df = pd.DataFrame({
        "country": ["Germany", "USA", "Germany", "Iran"],
        "total_price": [100, 200, 300, 400],
    })

    result = revenue_by_country(df)

    assert result["Germany"] == 400
    assert result["USA"] == 200
    assert result["Iran"] == 400