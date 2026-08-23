
from sqlalchemy import text

from data_platform.connector.connection_registry import get_connection
from data_platform.util.file_utils import read_text_files


def execute_sql(connection_name: str, *queries: str):
    with get_connection(connection_name).begin() as connection:
        for query in queries:
            connection.execute(text(query))

        connection.commit()


def run_sql_files(connection_name: str, file_names: list[str]) -> None:
    execute_sql(connection_name, *read_text_files(file_names))
