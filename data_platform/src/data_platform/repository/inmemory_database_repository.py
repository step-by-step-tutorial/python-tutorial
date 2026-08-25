import pandas

from data_platform.model.endpoints import DatabaseEndpoint
from data_platform.registry.connection_registry import connection_registry
from data_platform.util.collection_utils import list_of_values
from data_platform.util.database_utils import execute_files


class InmemoryDatabaseRepository:
    def __init__(self, endpoint: DatabaseEndpoint) -> None:
        self._endpoint = endpoint
        self._connection_name = endpoint.connection_name

    def truncate_stage_table(self) -> None:
        execute_files(self._connection_name, list_of_values(self._endpoint.truncate_sql_files))

    def execute_files(self, file_names: list[str]) -> None:
        execute_files(self._connection_name, file_names)

    def save(self, dataframe: pandas.DataFrame) -> None:
        with connection_registry.get_item(self._connection_name).begin() as connection:
            dataframe.to_sql(
                name=self._endpoint.stage_table_name,
                con=connection,
                schema=self._endpoint.schema or None,
                if_exists="append",
                index=False,
            )

    def replace(self, dataframe: pandas.DataFrame) -> None:
        self.truncate_stage_table()
        self.save(dataframe)
        self.execute_files(list_of_values(self._endpoint.write_sql_files))

