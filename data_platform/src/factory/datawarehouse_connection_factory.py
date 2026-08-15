import clickhouse_connect

from app_config import env_config as ec

def create_connection():
    return clickhouse_connect.get_client(
        host=ec.APP_DATAWAREHOUSE_HOST,
        port=ec.APP_DATAWAREHOUSE_PORT,
        database=ec.APP_DATAWAREHOUSE_NAME,
        username=ec.APP_DATAWAREHOUSE_USER,
        password=ec.APP_DATAWAREHOUSE_PASSWORD,
    )
