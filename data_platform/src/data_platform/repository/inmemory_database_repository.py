from typing import Any

from pandas import DataFrame

from data_platform.model.endpoints import DatabaseEndpoint
from data_platform.registry.connection_registry import connection_registry
from data_platform.util.collection_utils import to_values
from data_platform.util.database_utils import execute_query_files, execute_select_query


class InmemoryDatabaseRepository:
    def __init__(self, endpoint: DatabaseEndpoint) -> None:
        self._endpoint = endpoint
        self._connection_name = endpoint.connection_name

    def find_by_query(self, query: str) -> tuple[dict[Any, Any], ...]:
        return execute_select_query(self._connection_name, query)

    def execute_query_files(self, file_names: tuple[str, ...]) -> None:
        execute_query_files(self._connection_name, file_names)

    def truncate_stage_table(self) -> None:
        execute_query_files(self._connection_name, tuple(to_values(self._endpoint.truncate_sql_files)))

    def write(self, dataframe: DataFrame) -> None:
        with connection_registry.get_item(self._connection_name).begin() as connection:
            dataframe.to_sql(
                name=self._endpoint.stage_table_name,
                con=connection,
                schema=self._endpoint.schema or None,
                if_exists="append",
                index=False,
            )

    def overwrite(self, dataframe: DataFrame) -> None:
        self.truncate_stage_table()
        self.write(dataframe)
        execute_query_files(self._connection_name, tuple(to_values(self._endpoint.write_sql_files)))
