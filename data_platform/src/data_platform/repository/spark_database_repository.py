from pyspark.sql import DataFrame

from data_platform.config.keys import Key
from data_platform.config.main_settings import settings
from data_platform.model.endpoints import DatabaseEndpoint
from data_platform.util.collection_utils import to_values
from data_platform.util.database_utils import execute_query_files


class SparkDatabaseRepository:
    def __init__(self, endpoint: DatabaseEndpoint) -> None:
        self._endpoint = endpoint
        self._connection_name = endpoint.connection_name

    def truncate_stage_table(self) -> None:
        execute_query_files(self._connection_name, tuple(self._endpoint.truncate_sql_files.values()))

    def execute_query_files(self, file_names: tuple[str, ...]) -> None:
        execute_query_files(self._connection_name, file_names)

    def write(self, dataframe: DataFrame) -> None:
        database_settings = settings.database[Key(self._connection_name)]
        (
            dataframe.write
            .format("jdbc")
            .option("url", database_settings.jdbc_url)
            .option("dbtable", self._endpoint.full_stage_table_name)
            .option("user", database_settings.user)
            .option("password", database_settings.password)
            .option("driver", database_settings.driver)
            .mode("append")
            .save()
        )

    def overwrite(self, dataframe: DataFrame) -> None:
        self.truncate_stage_table()
        self.write(dataframe)
        self.execute_query_files(tuple(to_values(self._endpoint.write_sql_files)))
