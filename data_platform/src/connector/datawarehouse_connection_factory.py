from __future__ import annotations

import atexit
from typing import Any, Callable

import clickhouse_connect

from config.settings import settings as main_settings

registry: dict[str, Any] = {}
factories: dict[str, Callable[[], Any]] = {}


def create_sale_connection():
    return clickhouse_connect.get_client(
        host=main_settings.datawarehouse["sale.datawarehouse"].host,
        port=main_settings.datawarehouse["sale.datawarehouse"].port,
        database=main_settings.datawarehouse["sale.datawarehouse"].database_name,
        username=main_settings.datawarehouse["sale.datawarehouse"].user,
        password=main_settings.datawarehouse["sale.datawarehouse"].password,
    )


def create_house_connection():
    return clickhouse_connect.get_client(
        host=main_settings.datawarehouse["house.datawarehouse"].host,
        port=main_settings.datawarehouse["house.datawarehouse"].port,
        database=main_settings.datawarehouse["house.datawarehouse"].database_name,
        username=main_settings.datawarehouse["house.datawarehouse"].user,
        password=main_settings.datawarehouse["house.datawarehouse"].password,
    )


def create_audit_connection():
    return clickhouse_connect.get_client(
        host=main_settings.datawarehouse["audit.datawarehouse"].host,
        port=main_settings.datawarehouse["audit.datawarehouse"].port,
        database=main_settings.datawarehouse["audit.datawarehouse"].database_name,
        username=main_settings.datawarehouse["audit.datawarehouse"].user,
        password=main_settings.datawarehouse["audit.datawarehouse"].password,
    )


factories["sale.datawarehouse"] = create_sale_connection
factories["house.datawarehouse"] = create_house_connection
factories["audit.datawarehouse"] = create_audit_connection


def get_connection(name: str):
    if name not in registry:
        registry[name] = factories[name]()
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
