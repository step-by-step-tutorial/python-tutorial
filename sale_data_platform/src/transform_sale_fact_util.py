import pandas as pd


def transform_sale_fact(df: pd.DataFrame) -> pd.DataFrame:
    schema = df.rename(columns={"product": "product_name"}).copy()
    schema = schema[
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
    schema["order_date"] = schema["order_date"].dt.date

    return schema
