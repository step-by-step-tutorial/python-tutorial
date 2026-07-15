
import clickhouse_connect
from pyspark.sql import DataFrame

from src import config


class SaleWarehouseRepository:
    def __init__(self) -> None:
        self.client = clickhouse_connect.get_client(
            host=config.WAREHOUSE_HOST,
            port=config.WAREHOUSE_HTTP_PORT,
            database=config.WAREHOUSE_DATABASE,
            username=config.WAREHOUSE_USER,
            password=config.WAREHOUSE_PASSWORD,
        )

    def replace_sale_fact(
        self,
        sale_warehouse_dataframe: DataFrame,
    ) -> None:
        sale_pandas_dataframe = (
            sale_warehouse_dataframe
            .orderBy("order_id")
            .toPandas()
        )

        self.client.command("TRUNCATE TABLE sale_fact")
        self.client.insert_df("sale_fact", sale_pandas_dataframe)

    def get_revenue_by_category(self):
        return self.client.query_df(
            '''
            SELECT
                category,
                sum(total_price) AS revenue
            FROM sale_fact
            GROUP BY category
            ORDER BY revenue DESC
            '''
        )

    def get_revenue_by_country(self):
        return self.client.query_df(
            '''
            SELECT
                country,
                sum(total_price) AS revenue
            FROM sale_fact
            GROUP BY country
            ORDER BY revenue DESC
            '''
        )
