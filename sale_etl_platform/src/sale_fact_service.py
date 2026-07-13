import pandas as pd

import clickhouse_service


class SaleFactService:
    def __init__(self):
        self.client = clickhouse_service.create_client()

    def populate(self, sale_fact_df: pd.DataFrame) -> None:
        self.client.command("TRUNCATE TABLE fact_sales")
        self.client.insert_df("fact_sales", sale_fact_df)

    def revenue_by_category(self) -> pd.DataFrame:
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

    def revenue_by_country(self) -> pd.DataFrame:
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
