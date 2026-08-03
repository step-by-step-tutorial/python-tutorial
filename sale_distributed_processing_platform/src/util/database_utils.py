from factory import database_connection_factory
from sqlalchemy import text

def execute_sql(*queries: str):
    with database_connection_factory.create_connection().begin() as connection:
            for query in queries:
                connection.execute(text(query))
            connection.commit()
