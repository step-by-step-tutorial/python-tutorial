from collections.abc import Callable
from typing import Any

import pandas

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
        dataframe: Any,
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


def lookup_population_strategy(dataframe: Any) -> Callable[..., None]:
    if isinstance(dataframe, pandas.DataFrame):
        return populate_stage_from_pandas

    try:
        from pyspark.sql import DataFrame as SparkDataFrame
    except ModuleNotFoundError:
        SparkDataFrame = None

    if SparkDataFrame is not None and isinstance(dataframe, SparkDataFrame):
        return populate_stage_from_spark

    raise TypeError(f"Unsupported DataFrame type: {type(dataframe).__name__}")


try:
    from pyspark.sql import DataFrame as SparkDataFrame
except ModuleNotFoundError:
    SparkDataFrame = None


POPULATION_FUNCTIONS: dict[type[Any], Callable[..., None]] = {pandas.DataFrame: populate_stage_from_pandas}
if SparkDataFrame is not None:
    POPULATION_FUNCTIONS[SparkDataFrame] = populate_stage_from_spark
