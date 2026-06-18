import pandas as pd


def get_total_revenue(df: pd.DataFrame) -> float:
    return df["total_price"].sum()


def get_average_order_value(df: pd.DataFrame) -> float:
    return df["total_price"].mean()


def get_revenue_by_category(df: pd.DataFrame) -> pd.Series:
    return df.groupby("category")["total_price"].sum().sort_values(ascending=False)


def get_revenue_by_country(df: pd.DataFrame) -> pd.Series:
    return df.groupby("country")["total_price"].sum().sort_values(ascending=False)


def get_top_products_by_quantity(df: pd.DataFrame) -> pd.Series:
    return df.groupby("product")["quantity"].sum().sort_values(ascending=False)
