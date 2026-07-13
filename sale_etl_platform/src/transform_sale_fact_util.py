import pandas as pd


def transform_sale_fact(df: pd.DataFrame) -> pd.DataFrame:
    sale_fact = df.rename(columns={"product": "product_name"}).copy()
    sale_fact = sale_fact[
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
    sale_fact["order_date"] = sale_fact["order_date"].dt.date

    return sale_fact
