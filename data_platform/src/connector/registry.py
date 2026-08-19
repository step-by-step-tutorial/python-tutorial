from __future__ import annotations

import atexit
from typing import Any, Callable

import connector.database_connections
import connector.datalake_connections
import connector.datawarehouse_connections
import connector.kafka_connections

registry: dict[str, Any] = {}
factories: dict[str, Callable[[], Any]] = {
    "sale.database": connector.database_connections.create_sale_connection,
    "house.database": connector.database_connections.create_house_connection,
    "audit.database": connector.database_connections.create_audit_connection,
    "sale.datalake": connector.datalake_connections.create_sale_connection,
    "house.datalake": connector.datalake_connections.create_house_connection,
    "audit.datalake": connector.datalake_connections.create_audit_connection,
    "sale.datawarehouse": connector.datawarehouse_connections.create_sale_connection,
    "house.datawarehouse": connector.datawarehouse_connections.create_house_connection,
    "audit.datawarehouse": connector.datawarehouse_connections.create_audit_connection,
    "sale.kafka.producer": connector.kafka_connections.create_sale_publisher_connection,
    "house.kafka.producer": connector.kafka_connections.create_house_publisher_connection,
    "audit.kafka.producer": connector.kafka_connections.create_audit_publisher_connection,
    "sale.kafka.listener": connector.kafka_connections.create_sale_listener_connection,
    "house.kafka.listener": connector.kafka_connections.create_house_listener_connection,
    "audit.kafka.listener": connector.kafka_connections.create_audit_listener_connection,
}


def get_connection(name: str) -> Any:
    if name not in registry:
        registry[name] = factories[name]()
    return registry[name]


def close_connection(name: str) -> None:
    connection = registry.pop(name, None)
    if connection is None:
        return

    if hasattr(connection, "flush") and callable(connection.flush):
        connection.flush()
    if hasattr(connection, "dispose") and callable(connection.dispose):
        connection.dispose()
    elif hasattr(connection, "close") and callable(connection.close):
        connection.close()


def close_all_connections() -> None:
    for name in list(registry):
        close_connection(name)


atexit.register(close_all_connections)
