import clickhouse_connect

from data_platform.config.keys import Key
from data_platform.config.main_settings import settings as main_settings


def create_sale_connection():
    return clickhouse_connect.get_client(
        host=main_settings.data_warehouse[Key.SALE_DATA_WAREHOUSE].host,
        port=main_settings.data_warehouse[Key.SALE_DATA_WAREHOUSE].port,
        database=main_settings.data_warehouse[Key.SALE_DATA_WAREHOUSE].database_name,
        username=main_settings.data_warehouse[Key.SALE_DATA_WAREHOUSE].user,
        password=main_settings.data_warehouse[Key.SALE_DATA_WAREHOUSE].password,
    )


def create_house_connection():
    return clickhouse_connect.get_client(
        host=main_settings.data_warehouse[Key.HOUSE_DATA_WAREHOUSE].host,
        port=main_settings.data_warehouse[Key.HOUSE_DATA_WAREHOUSE].port,
        database=main_settings.data_warehouse[Key.HOUSE_DATA_WAREHOUSE].database_name,
        username=main_settings.data_warehouse[Key.HOUSE_DATA_WAREHOUSE].user,
        password=main_settings.data_warehouse[Key.HOUSE_DATA_WAREHOUSE].password,
    )


def create_online_shopping_connection():
    settings = main_settings.data_warehouse[Key.ONLINE_SHOPPING_DATA_WAREHOUSE]
    return clickhouse_connect.get_client(host=settings.host, port=settings.port, database=settings.database_name,
                                         username=settings.user, password=settings.password)


def create_audit_connection():
    return clickhouse_connect.get_client(
        host=main_settings.data_warehouse[Key.AUDIT_DATA_WAREHOUSE].host,
        port=main_settings.data_warehouse[Key.AUDIT_DATA_WAREHOUSE].port,
        database=main_settings.data_warehouse[Key.AUDIT_DATA_WAREHOUSE].database_name,
        username=main_settings.data_warehouse[Key.AUDIT_DATA_WAREHOUSE].user,
        password=main_settings.data_warehouse[Key.AUDIT_DATA_WAREHOUSE].password,
    )

