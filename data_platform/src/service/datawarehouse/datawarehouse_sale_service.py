from typing import Mapping

from pandas import DataFrame

from app_config import env_config as ec
from app_config.datawarehouse_schema import SALE_TABLE
from dataset.definition import DataWarehouse
from dataset.sale.datawarehouse_query import Queries
from factory import datawarehouse_connection_factory


def truncate_and_populate(datawarehouse: DataWarehouse, dataframe: DataFrame) -> None:
    with datawarehouse_connection_factory.create_connection() as connection:
        for query in datawarehouse.preparing_sql_files.values():
            connection.command(query)

        connection.insert_df(table=datawarehouse.full_table_name, df=dataframe)


def analyze(datawarehouse: DataWarehouse) -> Mapping[str, DataFrame]:
    result = {}

    with datawarehouse_connection_factory.create_connection() as connection:
        for key, query in datawarehouse.analysis_sql_files.items():
            result[key] = connection.query_df(query)

        return result

# TODO: the rest functions must remove
def populate(dataframe: DataFrame) -> None:
    with datawarehouse_connection_factory.create_connection() as connection:
        connection.command(Queries.TRUNCATE_DATAWAREHOUSE)
        connection.insert_df(table=f"{ec.DATAWAREHOUSE_NAME}.{SALE_TABLE}", df=dataframe)


def execute_query(query: str) -> DataFrame:
    with datawarehouse_connection_factory.create_connection() as connection:
        return connection.query_df(query)


def get_revenue_by_category() -> DataFrame:
    return execute_query(Queries.SELECT_REVENUE_BY_CATEGORY)


def get_revenue_by_country() -> DataFrame:
    return execute_query(Queries.SELECT_REVENUE_BY_COUNTRY)
