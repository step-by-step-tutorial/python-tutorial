import clickhouse_connect

from config.datawarehouse import settings as datawarehouse_settings


def create_connection():
    return clickhouse_connect.get_client(
        host=datawarehouse_settings.host,
        port=datawarehouse_settings.port,
        database=datawarehouse_settings.database_name,
        username=datawarehouse_settings.user,
        password=datawarehouse_settings.password,
    )
