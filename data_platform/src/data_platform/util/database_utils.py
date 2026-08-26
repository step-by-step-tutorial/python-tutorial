from typing import Any

from sqlalchemy import text

from data_platform.registry.connection_registry import connection_registry
from data_platform.util.file_utils import read_text_files


def execute_select_query(connection_name: str, query: str) -> tuple[dict[Any, Any], ...]:
    with connection_registry.get_item(connection_name).begin() as connection:
        result = connection.execute(text(query))
        rows = tuple(dict(row) for row in result.mappings().all())
        connection.commit()
    return rows


def execute_query_strings(connection_name: str, queries: tuple[str, ...]) -> None:
    with connection_registry.get_item(connection_name).begin() as connection:
        for query in queries:
            connection.execute(text(query))

        connection.commit()


def execute_query_files(connection_name: str, file_names: tuple[str, ...]) -> None:
    execute_query_strings(connection_name, read_text_files(file_names))
