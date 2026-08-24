from pyspark.sql import DataFrame

from data_platform.config.keys import Key
from data_platform.config.main_settings import settings as main_settings
from data_platform.model import DatabaseEndpoint
from data_platform.persistence.database_repository import DatabaseRepository
from data_platform.util.collection_utils import list_of_values


class SparkDatabaseRepository(DatabaseRepository):
    def __init__(self, endpoint: DatabaseEndpoint) -> None:
        super().__init__(endpoint)

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

