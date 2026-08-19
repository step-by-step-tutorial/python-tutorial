from __future__ import annotations

from collections.abc import Mapping

import pandas
import pyspark

from config.settings import settings as main_settings
from dataset.definition import DatabaseEndpoint
from keys import Key

from connector.registry import get_connection
from util.database_utils import execute_sql
from util.file_utils import read_text_file


DATABASE_SETTINGS = {
    Key.SALE_DATABASE: main_settings.database[Key.SALE_DATABASE],
    Key.HOUSE_DATABASE: main_settings.database[Key.HOUSE_DATABASE],
    Key.AUDIT_DATABASE: main_settings.database[Key.AUDIT_DATABASE],
}


class DatabaseRepository:
    def __init__(self, database: DatabaseEndpoint) -> None:
        self.database = database
        self.connection_name = database.connection_name

    def run_sql_files(self, sql_files: Mapping[str, str]) -> None:
        if not sql_files:
            return

        execute_sql(self.connection_name, *(read_text_file(file_name) for file_name in sql_files.values()))

    def truncate_stage_table(self) -> None:
        self.run_sql_files(self.database.truncate_sql_files)

    def populate_stage_table_from_memory(self, dataframe: pandas.DataFrame) -> None:
        with get_connection(self.connection_name).begin() as connection:
            dataframe.to_sql(
                name=self.database.stage_table_name,
                con=connection,
                schema=self.database.schema or None,
                if_exists="append",
                index=False,
            )

    def populate_stage_table_from_spark(self, dataframe: pyspark.sql.DataFrame) -> None:
        connection_settings = DATABASE_SETTINGS[self.connection_name]
        (
            dataframe.write
            .format("jdbc")
            .option("url", connection_settings.jdbc_url)
            .option("dbtable", self.database.full_stage_table_name)
            .option("user", connection_settings.user)
            .option("password", connection_settings.password)
            .option("driver", connection_settings.driver)
            .mode("append")
            .save()
        )

    def populate_stage_from_memory(self, dataframe: pandas.DataFrame) -> None:
        self.populate_stage_table_from_memory(dataframe)

    def populate_stage_from_spark(self, dataframe: pyspark.sql.DataFrame) -> None:
        self.populate_stage_table_from_spark(dataframe)

    def truncate_and_populate_from_memory(self, dataframe: pandas.DataFrame) -> None:
        self.truncate_stage_table()
        self.populate_stage_from_memory(dataframe)
        self.run_sql_files(self.database.write_sql_files)

    def truncate_and_populate_from_spark(self, dataframe: pyspark.sql.DataFrame) -> None:
        self.truncate_stage_table()
        self.populate_stage_from_spark(dataframe)
        self.run_sql_files(self.database.write_sql_files)
