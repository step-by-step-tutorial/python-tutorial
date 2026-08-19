from __future__ import annotations

import pandas
import pyspark

from config.settings import settings as main_settings
from connector.registry import get_connection
from dataset.definition import DatabaseEndpoint
from keys import Key
from util.collection_utils import list_of_values
from util.database_utils import run_sql_files


class DatabaseRepository:
    def __init__(self, endpoint: DatabaseEndpoint) -> None:
        self._endpoint = endpoint
        self._connection_name = endpoint.connection_name

    def truncate_stage_table(self) -> None:
        run_sql_files(self._connection_name, list_of_values(self._endpoint.truncate_sql_files))

    def populate_stage_table_from_memory(self, dataframe: pandas.DataFrame) -> None:
        with get_connection(self._connection_name).begin() as connection:
            dataframe.to_sql(
                name=self._endpoint.stage_table_name,
                con=connection,
                schema=self._endpoint.schema or None,
                if_exists="append",
                index=False,
            )

    def populate_stage_table_from_spark(self, dataframe: pyspark.sql.DataFrame) -> None:
        connection_settings = main_settings.database[Key(self._connection_name)]
        (
            dataframe.write
            .format("jdbc")
            .option("url", connection_settings.jdbc_url)
            .option("dbtable", self._endpoint.full_stage_table_name)
            .option("user", connection_settings.user)
            .option("password", connection_settings.password)
            .option("driver", connection_settings.driver)
            .mode("append")
            .save()
        )

    def truncate_and_populate_from_memory(self, dataframe: pandas.DataFrame) -> None:
        self.truncate_stage_table()
        self.populate_stage_table_from_memory(dataframe)
        run_sql_files(self._connection_name, list_of_values(self._endpoint.write_sql_files))

    def truncate_and_populate_from_spark(self, dataframe: pyspark.sql.DataFrame) -> None:
        self.truncate_stage_table()
        self.populate_stage_table_from_spark(dataframe)
        run_sql_files(self._connection_name, list_of_values(self._endpoint.write_sql_files))
