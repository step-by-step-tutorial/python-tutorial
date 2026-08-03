from collections.abc import Callable
from typing import Any

import pandas
import pyspark.sql

from app_config import env_config as ec
from factory import database_connection_factory


def populate_stage_from_pandas(dataframe: pandas.DataFrame) -> None:
    with database_connection_factory.create_connection().begin() as connection:
        dataframe.to_sql(
            name=ec.DATABASE_STAGE_TABLE_NAME,
            con=connection,
            if_exists="append",
            index=False,
        )


def populate_stage_from_spark(dataframe: pyspark.sql.DataFrame) -> None:
    (
        dataframe.write
        .format("jdbc")
        .option("url", ec.DATABASE_JDBC_URL)
        .option("dbtable", ec.DATABASE_STAGE_TABLE_NAME)
        .option("user", ec.DATABASE_USER)
        .option("password", ec.DATABASE_PASSWORD)
        .option("driver", ec.DATABASE_DRIVER)
        .mode("append")
        .save()
    )


POPULATION_FUNCTIONS: dict[type[Any], Callable[[Any], None]] = {
    pandas.DataFrame: populate_stage_from_pandas,
    pyspark.sql.DataFrame: populate_stage_from_spark,
}
