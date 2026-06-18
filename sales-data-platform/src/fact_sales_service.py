import time

import clickhouse_connect
import pandas as pd
from clickhouse_connect.driver.exceptions import OperationalError


class FactSalesService:
    def __init__(self, host: str, port: int, username: str, password: str):
        self.client = self._create_client(host=host, port=port, username=username, password=password)

    def _create_client(self, host: str, port: int, username: str, password: str):
        retries = 10
        retry_delay_seconds = 3.0

        for attempt in range(1, retries + 1):
            try:
                return clickhouse_connect.get_client(host=host, port=port, username=username, password=password)
            except OperationalError:
                if attempt == retries:
                    raise
                time.sleep(retry_delay_seconds)
        return None

    def populate_fact_sales(self, warehouse_df: pd.DataFrame) -> None:
        self.client.command("TRUNCATE TABLE sales_warehouse.fact_sales")
        self.client.insert_df("sales_warehouse.fact_sales",warehouse_df)

    def revenue_by_category(self) -> pd.DataFrame:
        return self.client.query_df(
            """
            SELECT category,
                   sum(total_price) AS revenue
            FROM sales_warehouse.fact_sales
            GROUP BY category
            ORDER BY revenue DESC
            """
        )

    def revenue_by_country(self) -> pd.DataFrame:
        return self.client.query_df(
            """
            SELECT country,
                   sum(total_price) AS revenue
            FROM sales_warehouse.fact_sales
            GROUP BY country
            ORDER BY revenue DESC
            """
        )
