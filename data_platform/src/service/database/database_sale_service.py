from typing import Any

from service.database.database_population_strategy import lookup_population_strategy
from util.database_utils import execute_sql
from util.file_utils import read_sql_file


class DatabaseQueries:
    TRUNCATE_STAGE_TABLE = read_sql_file("truncate_database_stage_table.sql")
    TRUNCATE_ALL_TABLES = read_sql_file("truncate_database_all_tables.sql")
    INSERT_CUSTOMERS = read_sql_file("insert_customers.sql")
    INSERT_PRODUCTS = read_sql_file("insert_products.sql")
    INSERT_ORDERS = read_sql_file("insert_orders.sql")
    INSERT_ORDER_ITEMS = read_sql_file("insert_order_items.sql")


def truncate_stage_table() -> None:
    execute_sql(DatabaseQueries.TRUNCATE_STAGE_TABLE)


def populate_stage_table(dataframe: Any) -> None:
    population_function = lookup_population_strategy(dataframe)
    population_function(dataframe)


def truncate_all_tables() -> None:
    execute_sql(DatabaseQueries.TRUNCATE_ALL_TABLES)


def populate_all_tables() -> None:
    execute_sql(
        DatabaseQueries.INSERT_CUSTOMERS,
        DatabaseQueries.INSERT_PRODUCTS,
        DatabaseQueries.INSERT_ORDERS,
        DatabaseQueries.INSERT_ORDER_ITEMS,
    )


def populate(dataframe: Any) -> None:
    truncate_stage_table()
    populate_stage_table(dataframe)
    truncate_all_tables()
    populate_all_tables()
