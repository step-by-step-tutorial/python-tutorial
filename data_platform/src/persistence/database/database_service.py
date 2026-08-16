from __future__ import annotations

from typing import cast

import pandas
import pyspark

from config.database import settings
from connector.database import postgres_connector as database_connection_factory
from dataset.definition import Dataset, DatabaseEndpoint
from util.database_utils import execute_sql
from util.file_utils import read_text_file


def run_sql_files(sql_files: tuple[str, ...]) -> None:
    if not sql_files:
        return

    execute_sql(*(read_text_file(file_name) for file_name in sql_files))


def populate_stage_from_pandas(dataset: Dataset, dataframe: pandas.DataFrame) -> None:
    database = cast(DatabaseEndpoint, dataset.get_destination("database"))
    with database_connection_factory.create_connection().begin() as connection:
        dataframe.to_sql(
            name=database.table_name,
            con=connection,
            if_exists="append",
            index=False,
        )


def populate_stage_from_spark(dataset: Dataset, dataframe: pyspark.sql.DataFrame) -> None:
    database = cast(DatabaseEndpoint, dataset.get_destination("database"))
    (
        dataframe.write
        .format("jdbc")
        .option("url", settings.jdbc_url)
        .option("dbtable", database.table_name)
        .option("user", settings.user)
        .option("password", settings.password)
        .option("driver", settings.driver)
        .mode("append")
        .save()
    )


def truncate_and_populate_from_pandas(dataset: Dataset, dataframe: pandas.DataFrame) -> None:
    database = cast(DatabaseEndpoint, dataset.get_destination("database"))
    run_sql_files(database.preparing_sql_files)
    populate_stage_from_pandas(dataset, dataframe)
    run_sql_files(database.analytical_sql_files)


def truncate_and_populate_from_spark(dataset: Dataset, dataframe: pyspark.sql.DataFrame) -> None:
    database = cast(DatabaseEndpoint, dataset.get_destination("database"))
    run_sql_files(database.preparing_sql_files)
    populate_stage_from_spark(dataset, dataframe)
    run_sql_files(database.analytical_sql_files)
