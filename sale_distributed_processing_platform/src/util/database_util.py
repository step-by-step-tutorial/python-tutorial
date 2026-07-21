from factory import database_connection_factory


def execute_sql(*queries: str):
    with database_connection_factory.create_connection() as connection:
        with connection.cursor() as cursor:
            for query in queries:
                cursor.execute(query)
