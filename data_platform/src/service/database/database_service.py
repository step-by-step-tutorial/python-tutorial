from __future__ import annotations

from typing import Any

from dataset.definition import Dataset
from service.database.database_population_strategy import lookup_population_strategy
from util.database_utils import execute_sql
from util.file_utils import read_text_file


def populate_stage_table(dataset: Dataset, dataframe: Any) -> None:
    population_function = lookup_population_strategy(dataframe)
    database = dataset.database

    if database.connection.jdbc_url and hasattr(dataframe, "write"):
        population_function(
            dataframe,
            database.table_name,
            database.connection.jdbc_url,
            database.connection.user,
            database.connection.password,
            database.connection.driver,
        )
        return

    population_function(dataframe, database.table_name)


def run_sql_files(sql_files: tuple[str, ...]) -> None:
    if not sql_files:
        return

    execute_sql(*(read_text_file(file_name) for file_name in sql_files))


def populate(dataset: Dataset, dataframe: Any) -> None:
    run_sql_files(dataset.database.before_load_sql_files)
    populate_stage_table(dataset, dataframe)
    run_sql_files(dataset.database.after_load_sql_files)
