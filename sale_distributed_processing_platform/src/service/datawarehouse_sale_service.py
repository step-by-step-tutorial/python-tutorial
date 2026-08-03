from pandas import DataFrame

from app_config import env_config as ec
from factory import datawarehouse_connection_factory
from util.text_file_utils import load_sql_query


class Queries:
    TRUNCATE_DATAWAREHOUSE = load_sql_query("truncate_datawarehouse.sql")
    SELECT_REVENUE_BY_CATEGORY = load_sql_query("select_revenue_by_category.sql")
    SELECT_REVENUE_BY_COUNTRY = load_sql_query("select_revenue_by_country.sql")


def populate(dataframe: DataFrame) -> None:
    with datawarehouse_connection_factory.create_connection() as connection:
        connection.command(Queries.TRUNCATE_DATAWAREHOUSE)
        connection.insert_df(table=ec.DATAWAREHOUSE_TABLE_NAME, df=dataframe)


def get_revenue_by_category() -> DataFrame:
    with datawarehouse_connection_factory.create_connection() as connection:
        return connection.query_df(Queries.SELECT_REVENUE_BY_CATEGORY)


def get_revenue_by_country() -> DataFrame:
    with datawarehouse_connection_factory.create_connection() as connection:
        return connection.query_df(Queries.SELECT_REVENUE_BY_COUNTRY)
