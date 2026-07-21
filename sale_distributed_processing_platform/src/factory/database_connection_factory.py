import psycopg2

from app_config import env_config as ec


def create_connection():
    return psycopg2.connect(
        host=ec.DATABASE_HOST,
        port=ec.DATABASE_PORT,
        dbname=ec.DATABASE_NAME,
        user=ec.DATABASE_USER,
        password=ec.DATABASE_PASSWORD,
    )
