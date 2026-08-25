from sqlalchemy import text

from typing import Any

from data_platform.registry.connection_registry import connection_registry
from data_platform.util.file_utils import read_text_files


def execute_query(connection_name: str, query: str) -> list[dict[Any, Any]]:
    with connection_registry.get_item(connection_name).begin() as connection:
        result = connection.execute(text(query))
        rows = [dict(row) for row in result.mappings().all()]
        connection.commit()
    return rows


def execute_queries(connection_name: str, *queries: str):
    with connection_registry.get_item(connection_name).begin() as connection:
        for query in queries:
            connection.execute(text(query))

        connection.commit()


def execute_files(connection_name: str, file_names: list[str]) -> None:
    execute_queries(connection_name, *read_text_files(file_names))
