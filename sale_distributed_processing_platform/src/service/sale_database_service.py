from pyspark.sql import DataFrame

from app_config import env_config as ec
from util.database_util import execute_sql
from util.file_util import load_sql_query


class Queries:
    TRUNCATE_SALE_STAGE_QUERY = load_sql_query("truncate_sale_stage.sql")
    TRUNCATE_NORMALIZED_TABLES = load_sql_query("truncate_normalized_tables.sql")
    INSERT_CUSTOMERS = load_sql_query("insert_customers.sql")
    INSERT_PRODUCTS = load_sql_query("insert_products.sql")
    INSERT_ORDERS = load_sql_query("insert_orders.sql")
    INSERT_ORDER_ITEMS = load_sql_query("insert_order_items.sql")


def populate_temporary_sale_table(dataframe: DataFrame) -> None:
    execute_sql(Queries.TRUNCATE_SALE_STAGE_QUERY)
    (
        dataframe
        .write
        .format("jdbc")
        .option("url", ec.DATABASE_URL)
        .option("dbtable", ec.DATABASE_SALE_STAGE_TABLE)
        .option("user", ec.DATABASE_USER)
        .option("password", ec.DATABASE_PASSWORD)
        .option("driver", ec.DATABASE_DRIVER)
        .mode("append")
        .save()
    )


def populate_sale_db() -> None:
    steps = [
        Queries.TRUNCATE_NORMALIZED_TABLES,
        Queries.INSERT_CUSTOMERS,
        Queries.INSERT_PRODUCTS,
        Queries.INSERT_ORDERS,
        Queries.INSERT_ORDER_ITEMS,
    ]

    execute_sql(*steps)


def populate(df: DataFrame) -> None:
    populate_temporary_sale_table(df)
    populate_sale_db()
