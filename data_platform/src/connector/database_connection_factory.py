from __future__ import annotations

import atexit
from typing import Any

from sqlalchemy import create_engine

from config.settings import settings as main_settings
registry: dict[str, Any] = {}


def create_sale_connection():
    return create_engine(main_settings.database["sale.database"].sqlalchemy_url)


def create_house_connection():
    return create_engine(main_settings.database["house.database"].sqlalchemy_url)


def create_audit_connection():
    return create_engine(main_settings.database["audit.database"].sqlalchemy_url)


registry["sale.database"] = create_sale_connection()
registry["house.database"] = create_house_connection()
registry["audit.database"] = create_audit_connection()


def get_connection(name: str):
    return registry[name]


def close_connection(name: str) -> None:
    connection = registry.pop(name, None)
    if connection is None:
        return

    if hasattr(connection, "dispose") and callable(connection.dispose):
        connection.dispose()
    elif hasattr(connection, "close") and callable(connection.close):
        connection.close()


def close_all_connections() -> None:
    for name in list(registry):
        close_connection(name)


atexit.register(close_all_connections)
