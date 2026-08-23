import clickhouse_connect

from data_platform.config.main_settings import settings as main_settings
from data_platform.config.keys import Key


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


def create_audit_connection():
    return clickhouse_connect.get_client(
        host=main_settings.data_warehouse[Key.AUDIT_DATA_WAREHOUSE].host,
        port=main_settings.data_warehouse[Key.AUDIT_DATA_WAREHOUSE].port,
        database=main_settings.data_warehouse[Key.AUDIT_DATA_WAREHOUSE].database_name,
        username=main_settings.data_warehouse[Key.AUDIT_DATA_WAREHOUSE].user,
        password=main_settings.data_warehouse[Key.AUDIT_DATA_WAREHOUSE].password,
    )
