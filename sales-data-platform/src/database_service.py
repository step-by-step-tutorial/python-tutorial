import pandas as pd
from sqlalchemy import create_engine, text


class DatabaseService:
    def __init__(self, url: str):
        self.engine = create_engine(url)

    def truncate(self) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    TRUNCATE TABLE order_items, orders, products, customers
                    RESTART IDENTITY CASCADE
                    """
                )
            )

    def populate(self, df: pd.DataFrame) -> None:
        self.truncate()

        customers = df[["customer_name", "country"]].drop_duplicates()

        products = df[["product", "category", "unit_price"]].drop_duplicates()
        products = products.rename(columns={"product": "product_name"})

        customers.to_sql("customers", self.engine, if_exists="append", index=False)
        products.to_sql("products", self.engine, if_exists="append", index=False, )

        with self.engine.begin() as connection:
            customers_db = pd.read_sql("SELECT * FROM customers", connection)
            products_db = pd.read_sql("SELECT * FROM products", connection)

            enriched_df = df.merge(customers_db, on=["customer_name", "country"])
            enriched_df = enriched_df.merge(
                products_db,
                left_on=["product", "category", "unit_price"],
                right_on=["product_name", "category", "unit_price"]
            )
            orders = enriched_df[["order_id", "customer_id", "order_date"]].drop_duplicates()

            order_items = enriched_df[
                [
                    "order_id",
                    "product_id",
                    "quantity",
                    "unit_price",
                    "total_price",
                ]
            ]

            orders.to_sql("orders", connection, if_exists="append", index=False)
            order_items.to_sql("order_items", connection, if_exists="append", index=False, )
