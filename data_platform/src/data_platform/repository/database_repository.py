from typing import Any

from data_platform.model.endpoints import DatabaseEndpoint
from data_platform.util.database_utils import execute_query_files, execute_select_query


class DatabaseRepository:
    def __init__(self, endpoint: DatabaseEndpoint) -> None:
        self._endpoint = endpoint
        self._connection_name = endpoint.connection_name

    def find_by_query(self, query: str) -> tuple[dict[Any, Any], ...]:
        return execute_select_query(self._connection_name, query)

    def execute_query_files(self, file_names: tuple[str, ...]) -> None:
        execute_query_files(self._connection_name, file_names)
