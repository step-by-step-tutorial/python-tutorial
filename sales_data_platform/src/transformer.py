import pandas as pd


def transform_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["total_price"] = df["quantity"] * df["unit_price"]
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month

    return df


def build_warehouse_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    warehouse_df = df.rename(columns={"product": "product_name"}).copy()

    warehouse_df = warehouse_df[
        [
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
    ]

    warehouse_df["order_date"] = warehouse_df["order_date"].dt.date

    return warehouse_df