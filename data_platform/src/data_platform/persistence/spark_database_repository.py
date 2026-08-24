from pyspark.sql import DataFrame

from data_platform.config.keys import Key
from data_platform.config.main_settings import settings as main_settings
from data_platform.model import DatabaseEndpoint
from data_platform.util.collection_utils import list_of_values
from data_platform.util.database_utils import execute_files


class SparkDatabaseRepository:
    def __init__(self, endpoint: DatabaseEndpoint) -> None:
        self._endpoint = endpoint
        self._connection_name = endpoint.connection_name

    def truncate_stage_table(self) -> None:
        execute_files(self._connection_name, list_of_values(self._endpoint.truncate_sql_files))

    def execute_files(self, file_names: list[str]) -> None:
        execute_files(self._connection_name, file_names)

    def save(self, dataframe: DataFrame) -> None:
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

    def replace(self, dataframe: DataFrame) -> None:
        self.truncate_stage_table()
        self.save(dataframe)
        self.execute_files(list_of_values(self._endpoint.write_sql_files))

