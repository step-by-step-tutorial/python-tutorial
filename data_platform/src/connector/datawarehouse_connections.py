from __future__ import annotations

import clickhouse_connect

from config.settings import settings as main_settings
from keys import Key


def create_sale_connection():
    return clickhouse_connect.get_client(
        host=main_settings.datawarehouse[Key.SALE_DATAWAREHOUSE].host,
        port=main_settings.datawarehouse[Key.SALE_DATAWAREHOUSE].port,
        database=main_settings.datawarehouse[Key.SALE_DATAWAREHOUSE].database_name,
        username=main_settings.datawarehouse[Key.SALE_DATAWAREHOUSE].user,
        password=main_settings.datawarehouse[Key.SALE_DATAWAREHOUSE].password,
    )


def create_house_connection():
    return clickhouse_connect.get_client(
        host=main_settings.datawarehouse[Key.HOUSE_DATAWAREHOUSE].host,
        port=main_settings.datawarehouse[Key.HOUSE_DATAWAREHOUSE].port,
        database=main_settings.datawarehouse[Key.HOUSE_DATAWAREHOUSE].database_name,
        username=main_settings.datawarehouse[Key.HOUSE_DATAWAREHOUSE].user,
        password=main_settings.datawarehouse[Key.HOUSE_DATAWAREHOUSE].password,
    )


def create_audit_connection():
    return clickhouse_connect.get_client(
        host=main_settings.datawarehouse[Key.AUDIT_DATAWAREHOUSE].host,
        port=main_settings.datawarehouse[Key.AUDIT_DATAWAREHOUSE].port,
        database=main_settings.datawarehouse[Key.AUDIT_DATAWAREHOUSE].database_name,
        username=main_settings.datawarehouse[Key.AUDIT_DATAWAREHOUSE].user,
        password=main_settings.datawarehouse[Key.AUDIT_DATAWAREHOUSE].password,
    )
