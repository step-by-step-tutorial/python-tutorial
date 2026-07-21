import clickhouse_connect

from app_config import env_config as ec

def create_connection():
    return clickhouse_connect.get_client(
        host=ec.DATAWAREHOUSE_HOST,
        port=ec.DATAWAREHOUSE_HTTP_PORT,
        database=ec.DATAWAREHOUSE_DATABASE,
        username=ec.DATAWAREHOUSE_USER,
        password=ec.DATAWAREHOUSE_PASSWORD,
    )
