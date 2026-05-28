import pandas as pd


def calculate_total_revenue(df: pd.DataFrame) -> float:
    return df["total_price"].sum()


def calculate_average_order_value(df: pd.DataFrame) -> float:
    return df["total_price"].mean()


def revenue_by_category(df: pd.DataFrame) -> pd.Series:
    return df.groupby("category")["total_price"].sum().sort_values(ascending=False)


def revenue_by_country(df: pd.DataFrame) -> pd.Series:
    return df.groupby("country")["total_price"].sum().sort_values(ascending=False)


def top_products_by_quantity(df: pd.DataFrame) -> pd.Series:
    return df.groupby("product")["quantity"].sum().sort_values(ascending=False)