from pandas import DataFrame

from factory import datawarehouse_connection_factory
from util.text_file_utils import load_sql_query


class Queries:
    TRUNCATE_SALE_FACT = load_sql_query("truncate_sale_fact.sql")
    SELECT_REVENUE_BY_CATEGORY = load_sql_query("select_revenue_by_category.sql")
    SELECT_REVENUE_BY_COUNTRY = load_sql_query("select_revenue_by_country.sql")


def populate(dataframe: DataFrame) -> None:
    with datawarehouse_connection_factory.create_connection() as connection:
        connection.command(Queries.TRUNCATE_SALE_FACT)
        connection.insert_df("sale_fact", dataframe)


def get_revenue_by_category() -> DataFrame:
    with datawarehouse_connection_factory.create_connection() as connection:
        return connection.query_df(Queries.SELECT_REVENUE_BY_CATEGORY)


def get_revenue_by_country() -> DataFrame:
    with datawarehouse_connection_factory.create_connection() as connection:
        return connection.query_df(Queries.SELECT_REVENUE_BY_COUNTRY)
