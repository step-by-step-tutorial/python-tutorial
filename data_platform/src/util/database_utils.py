from sqlalchemy import text

from connector.database.postgres_connector import create_connection


def execute_sql(*queries: str):
    with create_connection().begin() as connection:
        for query in queries:
            connection.execute(text(query))
        connection.commit()
