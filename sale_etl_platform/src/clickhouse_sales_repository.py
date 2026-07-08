import pandas as pd
import clickhouse_connect


class ClickHouseSalesRepository:
    def __init__(
            self,
            host: str,
            port: int,
            database: str,
            username: str,
            password: str,
    ):
        self.client = clickhouse_connect.get_client(
            host=host,
            port=port,
            database=database,
            username=username,
            password=password,
        )

    def load_sales_fact_data(
            self,
            sales_warehouse_dataframe: pd.DataFrame,
    ) -> None:
        self.client.command("TRUNCATE TABLE fact_sales")

        self.client.insert_df(
            "fact_sales",
            sales_warehouse_dataframe,
        )

    def get_revenue_by_category(self) -> pd.DataFrame:
        return self.client.query_df(
            """
            SELECT
                category,
                sum(total_price) AS revenue
            FROM fact_sales
            GROUP BY category
            ORDER BY revenue DESC
            """
        )

    def get_revenue_by_country(self) -> pd.DataFrame:
        return self.client.query_df(
            """
            SELECT
                country,
                sum(total_price) AS revenue
            FROM fact_sales
            GROUP BY country
            ORDER BY revenue DESC
            """
        )