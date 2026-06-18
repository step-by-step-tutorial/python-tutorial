import time

import pandas as pd
import clickhouse_connect
from clickhouse_connect.driver.exceptions import OperationalError


class ClickHouseLoader:
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        retries: int = 10,
        retry_delay_seconds: float = 3.0,
    ):
        self.client = self._connect(
            host=host,
            port=port,
            username=username,
            password=password,
            retries=retries,
            retry_delay_seconds=retry_delay_seconds,
        )

    def _connect(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        retries: int,
        retry_delay_seconds: float,
    ):
        for attempt in range(1, retries + 1):
            try:
                return clickhouse_connect.get_client(
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                )
            except OperationalError:
                if attempt == retries:
                    raise
                time.sleep(retry_delay_seconds)

    def load_fact_sales(self, warehouse_df: pd.DataFrame) -> None:
        self.client.command("TRUNCATE TABLE sales_warehouse.fact_sales")

        self.client.insert_df(
            "sales_warehouse.fact_sales",
            warehouse_df,
        )

    def revenue_by_category(self) -> pd.DataFrame:
        return self.client.query_df(
            """
            SELECT
                category,
                sum(total_price) AS revenue
            FROM sales_warehouse.fact_sales
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
            FROM sales_warehouse.fact_sales
            GROUP BY country
            ORDER BY revenue DESC
            """
        )
