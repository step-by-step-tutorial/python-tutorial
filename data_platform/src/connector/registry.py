from __future__ import annotations

import atexit
from typing import Any, Callable

import connector.database_connections
import connector.datalake_connections
import connector.datawarehouse_connections
import connector.kafka_connections

from keys import Key

registry: dict[str, Any] = {}
factories: dict[str, Callable[[], Any]] = {
    Key.SALE_DATABASE: connector.database_connections.create_sale_connection,
    Key.HOUSE_DATABASE: connector.database_connections.create_house_connection,
    Key.AUDIT_DATABASE: connector.database_connections.create_audit_connection,
    Key.SALE_DATALAKE: connector.datalake_connections.create_sale_connection,
    Key.HOUSE_DATALAKE: connector.datalake_connections.create_house_connection,
    Key.AUDIT_DATALAKE: connector.datalake_connections.create_audit_connection,
    Key.SALE_DATAWAREHOUSE: connector.datawarehouse_connections.create_sale_connection,
    Key.HOUSE_DATAWAREHOUSE: connector.datawarehouse_connections.create_house_connection,
    Key.AUDIT_DATAWAREHOUSE: connector.datawarehouse_connections.create_audit_connection,
    Key.SALE_KAFKA_PRODUCER: connector.kafka_connections.create_sale_publisher_connection,
    Key.HOUSE_KAFKA_PRODUCER: connector.kafka_connections.create_house_publisher_connection,
    Key.AUDIT_KAFKA_PRODUCER: connector.kafka_connections.create_audit_publisher_connection,
    Key.SALE_KAFKA_LISTENER: connector.kafka_connections.create_sale_listener_connection,
    Key.HOUSE_KAFKA_LISTENER: connector.kafka_connections.create_house_listener_connection,
    Key.AUDIT_KAFKA_LISTENER: connector.kafka_connections.create_audit_listener_connection,
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
