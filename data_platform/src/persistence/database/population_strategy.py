from collections.abc import Callable
from typing import Any

import pandas
import pyspark.sql

from connector.database import postgres_connector as database_connection_factory


def populate_stage_from_pandas(dataframe: pandas.DataFrame, table_name: str) -> None:
    with database_connection_factory.create_connection().begin() as connection:
        dataframe.to_sql(
            name=table_name,
            con=connection,
            if_exists="append",
            index=False,
        )


def populate_stage_from_spark(
        dataframe: pyspark.sql.DataFrame,
        table_name: str,
        jdbc_url: str,
        user: str,
        password: str,
        driver: str,
) -> None:
    (
        dataframe.write
        .format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", table_name)
        .option("user", user)
        .option("password", password)
        .option("driver", driver)
        .mode("append")
        .save()
    )


POPULATION_FUNCTIONS: dict[type[Any], Callable[..., None]] = {
    pandas.DataFrame: populate_stage_from_pandas,
    pyspark.sql.DataFrame: populate_stage_from_spark,
}


def lookup_population_strategy(dataframe: Any) -> Callable[..., None]:
    dataframe_type = type(dataframe)

    for registered_type, function in POPULATION_FUNCTIONS.items():
        if issubclass(dataframe_type, registered_type):
            return function

    raise TypeError(f"Unsupported DataFrame type: {dataframe_type.__name__}")
