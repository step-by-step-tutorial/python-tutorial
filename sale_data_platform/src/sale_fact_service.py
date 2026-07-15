import pandas as pd

import datawarehouse_service


class SaleFactService:
    def __init__(self):
        self.client = datawarehouse_service.create_client()

    def populate(self, warehouse_df: pd.DataFrame) -> None:
        self.client.command("TRUNCATE TABLE sale_warehouse.sale_fact")
        self.client.insert_df("sale_warehouse.sale_fact", warehouse_df)

    def revenue_by_category(self) -> pd.DataFrame:
        return self.client.query_df(
            """
            SELECT category, sum(total_price) AS revenue
            FROM sale_warehouse.sale_fact
            GROUP BY category
            ORDER BY revenue DESC
            """
        )

    def revenue_by_country(self) -> pd.DataFrame:
        return self.client.query_df(
            """
            SELECT country, sum(total_price) AS revenue
            FROM sale_warehouse.sale_fact
            GROUP BY country
            ORDER BY revenue DESC
            """
        )
