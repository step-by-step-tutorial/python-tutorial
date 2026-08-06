from pandas import DataFrame

from app_config import env_config as ec
from app_config.datawarehouse_schema import SALE_TABLE
from factory import datawarehouse_connection_factory
from util.file_utils import read_sql_file


class Queries:
    TRUNCATE_DATAWAREHOUSE = read_sql_file("truncate_datawarehouse.sql")
    SELECT_REVENUE_BY_CATEGORY = read_sql_file("select_revenue_by_category.sql")
    SELECT_REVENUE_BY_COUNTRY = read_sql_file("select_revenue_by_country.sql")


def populate(dataframe: DataFrame) -> None:
    with datawarehouse_connection_factory.create_connection() as connection:
        connection.command(Queries.TRUNCATE_DATAWAREHOUSE)
        connection.insert_df(table=f"{ec.DATAWAREHOUSE_NAME}.{SALE_TABLE}", df=dataframe)


def get_revenue_by_category() -> DataFrame:
    with datawarehouse_connection_factory.create_connection() as connection:
        return connection.query_df(Queries.SELECT_REVENUE_BY_CATEGORY)


def get_revenue_by_country() -> DataFrame:
    with datawarehouse_connection_factory.create_connection() as connection:
        return connection.query_df(Queries.SELECT_REVENUE_BY_COUNTRY)
