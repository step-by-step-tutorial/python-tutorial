
import clickhouse_connect

from data_platform.config.main_settings import settings as main_settings
from data_platform.keys import Key


def create_sale_connection():
    return clickhouse_connect.get_client(
        host=main_settings.data_warehouse[Key.SALE_DATAWAREHOUSE].host,
        port=main_settings.data_warehouse[Key.SALE_DATAWAREHOUSE].port,
        database=main_settings.data_warehouse[Key.SALE_DATAWAREHOUSE].database_name,
        username=main_settings.data_warehouse[Key.SALE_DATAWAREHOUSE].user,
        password=main_settings.data_warehouse[Key.SALE_DATAWAREHOUSE].password,
    )


def create_house_connection():
    return clickhouse_connect.get_client(
        host=main_settings.data_warehouse[Key.HOUSE_DATAWAREHOUSE].host,
        port=main_settings.data_warehouse[Key.HOUSE_DATAWAREHOUSE].port,
        database=main_settings.data_warehouse[Key.HOUSE_DATAWAREHOUSE].database_name,
        username=main_settings.data_warehouse[Key.HOUSE_DATAWAREHOUSE].user,
        password=main_settings.data_warehouse[Key.HOUSE_DATAWAREHOUSE].password,
    )


def create_audit_connection():
    return clickhouse_connect.get_client(
        host=main_settings.data_warehouse[Key.AUDIT_DATAWAREHOUSE].host,
        port=main_settings.data_warehouse[Key.AUDIT_DATAWAREHOUSE].port,
        database=main_settings.data_warehouse[Key.AUDIT_DATAWAREHOUSE].database_name,
        username=main_settings.data_warehouse[Key.AUDIT_DATAWAREHOUSE].user,
        password=main_settings.data_warehouse[Key.AUDIT_DATAWAREHOUSE].password,
    )
