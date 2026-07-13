import pandas as pd


def transform_sale_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["total_price"] = df["quantity"] * df["unit_price"]
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month

    return df