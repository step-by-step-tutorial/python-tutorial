from __future__ import annotations

import atexit
from typing import Any

import clickhouse_connect

from config.datawarehouse import audit_settings, house_settings, sale_settings

registry: dict[str, Any] = {}


def create_sale_connection():
    return clickhouse_connect.get_client(
        host=sale_settings.host,
        port=sale_settings.port,
        database=sale_settings.database_name,
        username=sale_settings.user,
        password=sale_settings.password,
    )


def create_house_connection():
    return clickhouse_connect.get_client(
        host=house_settings.host,
        port=house_settings.port,
        database=house_settings.database_name,
        username=house_settings.user,
        password=house_settings.password,
    )


def create_audit_connection():
    return clickhouse_connect.get_client(
        host=audit_settings.host,
        port=audit_settings.port,
        database=audit_settings.database_name,
        username=audit_settings.user,
        password=audit_settings.password,
    )


registry["sale.datawarehouse"] = create_sale_connection()
registry["house.datawarehouse"] = create_house_connection()
registry["audit.datawarehouse"] = create_audit_connection()


def get_connection(name: str):
    return registry[name]


def close_connection(name: str) -> None:
    connection = registry.pop(name, None)
    if connection is None:
        return

    if hasattr(connection, "close") and callable(connection.close):
        connection.close()
    elif hasattr(connection, "dispose") and callable(connection.dispose):
        connection.dispose()


def close_all_connections() -> None:
    for name in list(registry):
        close_connection(name)


atexit.register(close_all_connections)
