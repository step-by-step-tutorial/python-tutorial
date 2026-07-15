
import psycopg2
from pyspark.sql import DataFrame

from src import config


class SalePostgresRepository:
    def replace_sale_data(
        self,
        transformed_sale_dataframe: DataFrame,
    ) -> None:
        self._truncate_sale_stage()
        self._append_sale_stage(transformed_sale_dataframe)
        self._normalize_sale_stage()

    def _truncate_sale_stage(self) -> None:
        with self._create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("TRUNCATE TABLE sale_stage")

    def _append_sale_stage(
        self,
        transformed_sale_dataframe: DataFrame,
    ) -> None:
        (
            transformed_sale_dataframe
            .write
            .format("jdbc")
            .option("url", config.DATABASE_JDBC_URL)
            .option("dbtable", "sale_stage")
            .option("user", config.DATABASE_USER)
            .option("password", config.DATABASE_PASSWORD)
            .option("driver", "org.postgresql.Driver")
            .mode("append")
            .save()
        )

    def _normalize_sale_stage(self) -> None:
        with self._create_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    '''
                    TRUNCATE TABLE
                        order_item,
                        sale_order,
                        product,
                        customer
                    RESTART IDENTITY CASCADE
                    '''
                )

                cursor.execute(
                    '''
                    INSERT INTO customer (
                        customer_name,
                        country
                    )
                    SELECT DISTINCT
                        customer_name,
                        country
                    FROM sale_stage
                    '''
                )

                cursor.execute(
                    '''
                    INSERT INTO product (
                        product_name,
                        category
                    )
                    SELECT DISTINCT
                        product_name,
                        category
                    FROM sale_stage
                    '''
                )

                cursor.execute(
                    '''
                    INSERT INTO sale_order (
                        order_id,
                        customer_id,
                        order_date
                    )
                    SELECT DISTINCT
                        sale_stage.order_id,
                        customer.customer_id,
                        sale_stage.order_date
                    FROM sale_stage
                    JOIN customer
                      ON customer.customer_name = sale_stage.customer_name
                     AND customer.country = sale_stage.country
                    '''
                )

                cursor.execute(
                    '''
                    INSERT INTO order_item (
                        order_id,
                        product_id,
                        quantity,
                        unit_price,
                        total_price
                    )
                    SELECT
                        sale_stage.order_id,
                        product.product_id,
                        sale_stage.quantity,
                        sale_stage.unit_price,
                        sale_stage.total_price
                    FROM sale_stage
                    JOIN product
                      ON product.product_name = sale_stage.product_name
                     AND product.category = sale_stage.category
                    '''
                )

    def _create_connection(self):
        return psycopg2.connect(
            host=config.DATABASE_HOST,
            port=config.DATABASE_PORT,
            dbname=config.DATABASE_DATABASE,
            user=config.DATABASE_USER,
            password=config.DATABASE_PASSWORD,
        )
