import pandas as pd

import clickhouse_service


class SaleFactService:
    def __init__(self):
        self.client = clickhouse_service.create_client()

    def populate(self, warehouse_df: pd.DataFrame) -> None:
        self.client.command("TRUNCATE TABLE sale_warehouse.fact_sale")
        self.client.insert_df("sale_warehouse.fact_sale", warehouse_df)

    def revenue_by_category(self) -> pd.DataFrame:
        return self.client.query_df(
            """
            SELECT category, sum(total_price) AS revenue
            FROM sale_warehouse.fact_sale
            GROUP BY category
            ORDER BY revenue DESC
            """
        )

    def revenue_by_country(self) -> pd.DataFrame:
        return self.client.query_df(
            """
            SELECT country, sum(total_price) AS revenue
            FROM sale_warehouse.fact_sale
            GROUP BY country
            ORDER BY revenue DESC
            """
        )
