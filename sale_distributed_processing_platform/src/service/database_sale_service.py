from typing import Any

from service.database_population_strategy import POPULATION_FUNCTIONS
from util.database_utils import execute_sql
from util.text_file_utils import load_sql_query


class DatabaseQueries:
    TRUNCATE_STAGE_TABLE = load_sql_query("truncate_database_stage_table.sql")
    TRUNCATE_ALL_TABLES = load_sql_query("truncate_database_all_tables.sql")
    INSERT_CUSTOMERS = load_sql_query("insert_customers.sql")
    INSERT_PRODUCTS = load_sql_query("insert_products.sql")
    INSERT_ORDERS = load_sql_query("insert_orders.sql")
    INSERT_ORDER_ITEMS = load_sql_query("insert_order_items.sql")


def truncate_stage_table() -> None:
    execute_sql(DatabaseQueries.TRUNCATE_STAGE_TABLE)


def populate_stage_table(dataframe: Any) -> None:
    try:
        population_function = POPULATION_FUNCTIONS[type(dataframe)]
    except KeyError as error:
        raise TypeError(f"Unsupported DataFrame type: {type(dataframe).__name__}") from error

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
