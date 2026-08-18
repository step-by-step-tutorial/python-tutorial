from sqlalchemy import text

from connector.database_connection_factory import get_connection


def execute_sql(*queries: str, connection_name: str):
    with get_connection(connection_name).begin() as connection:
        for query in queries:
            connection.execute(text(query))
        connection.commit()
