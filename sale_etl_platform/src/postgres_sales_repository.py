import pandas as pd
from sqlalchemy import create_engine, text


class PostgresSalesRepository:
    def __init__(self, postgres_url: str):
        self.engine = create_engine(postgres_url)

    def clear_sales_tables(self) -> None:
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    """
                    TRUNCATE TABLE order_items, orders, products, customers
                    RESTART IDENTITY CASCADE
                    """
                )
            )

    def load_sales_data(self, sales_dataframe: pd.DataFrame) -> None:
        self.clear_sales_tables()

        customers_dataframe = sales_dataframe[
            ["customer_name", "country"]
        ].drop_duplicates()

        products_dataframe = sales_dataframe[
            ["product", "category", "unit_price"]
        ].drop_duplicates()

        products_dataframe = products_dataframe.rename(
            columns={"product": "product_name"}
        )

        customers_dataframe.to_sql(
            "customers",
            self.engine,
            if_exists="append",
            index=False,
        )

        products_dataframe.to_sql(
            "products",
            self.engine,
            if_exists="append",
            index=False,
        )

        with self.engine.begin() as connection:
            persisted_customers_dataframe = pd.read_sql(
                "SELECT * FROM customers",
                connection,
            )

            persisted_products_dataframe = pd.read_sql(
                "SELECT * FROM products",
                connection,
            )

            enriched_sales_dataframe = sales_dataframe.merge(
                persisted_customers_dataframe,
                on=["customer_name", "country"],
            )

            enriched_sales_dataframe = enriched_sales_dataframe.merge(
                persisted_products_dataframe,
                left_on=["product", "category", "unit_price"],
                right_on=["product_name", "category", "unit_price"],
            )

            orders_dataframe = enriched_sales_dataframe[
                ["order_id", "customer_id", "order_date"]
            ].drop_duplicates()

            order_items_dataframe = enriched_sales_dataframe[
                [
                    "order_id",
                    "product_id",
                    "quantity",
                    "unit_price",
                    "total_price",
                ]
            ]

            orders_dataframe.to_sql(
                "orders",
                connection,
                if_exists="append",
                index=False,
            )

            order_items_dataframe.to_sql(
                "order_items",
                connection,
                if_exists="append",
                index=False,
            )