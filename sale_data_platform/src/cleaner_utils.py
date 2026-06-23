import pandas as pd


def clean_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    df["quantity"] = df["quantity"].fillna(1)
    df["unit_price"] = df["unit_price"].fillna(df["unit_price"].mean())

    df = df.dropna(subset=["order_date"])

    return df